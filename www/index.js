// Page loading stuff goes at the top here


// Tired programmers can have a little global scope... as a treat
// old_groups is just here to check if changes have been made
let groups;
let old_groups;
let mod_mode;
// Use URL access token if exists
// Of course Reddit returns a parameter string with broken formatting
let fixedURLParams = new URLSearchParams("?"+window.location.hash.slice(1));
let access_token = fixedURLParams.get("access_token");
// How the fuck is this not built-in to JS? Copied from StackOverflow:
// https://stackoverflow.com/a/25490531
const getCookieValue = (name) => (
  document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')?.pop() || ''
)
// Save URL access token if we have one, and users have opted in
// Fun fact, this checkbox means I don't need a "we use cookies" popup for GDPR compliance
if (getCookieValue("user_pinger_2_remember_me") && access_token) {
    document.cookie = "access_token = " + access_token + "; SameSite=Strict";
}
// If we don't have an access token use our saved one
if (!access_token && getCookieValue("access_token")) {
    access_token = getCookieValue("access_token");
}
// No access token in URL or cookies? send to login page
if (!access_token) {
    location.href = "login.html";
}

// Apparently this is halal now, provided you defer the script
// No more window.onload
load_page();


function load_page() {
    document.getElementById("toggle-mod-mode").checked = false;
    document.getElementById("all-mode-button").checked = true;
    fetch(
        `api/me?access_token=${access_token}`
    ).then((response) => {
        if (response.status != "200") {
            // If the user's login doesn't work, make 'em get a new one
            location.href = "login.html";
        }
        return response.json();
    }).then((data) => {
        username = data;
        document.getElementById("welcome").textContent = "Hello /u/"+username+",";
        fetch(`api/list_groups?access_token=${access_token}`)
            .then((response) => {
                if (response.status != "200") {
                    alert("Unknown error fetching groups. Please contact support")
                }
                return response.json();
            })
            .then((data) => {
                document.getElementById("save-prompt").classList.remove("loading");
                groups = data;
                old_groups = JSON.parse(JSON.stringify(groups));
                build_group_table(data);
            });
    });
}


// TAB BAR FUNCTIONS


function toggle_mod_mode(checkbox) {
    mod_mode = checkbox.checked;
    build_group_table(groups);
    toggle_all_tab();
    let els = document.getElementsByClassName("mod-only");
    for (var i = 0; i < els.length; i++) {
        els[i].style.display = els[i].style.display == "none" ? "" : "none";
    }
}


// input radio button onchange events don't fire when they are unchecked
// hence why each of these functions hides the contents of other tabs.
// That's stupid, right? Unchecking is a change, why wouldn't it fire?
//
// "Ah yes, radio buttons, what a convenient way to have several
// mutually-exclusive webpage states"
// -me, a fucking moron apparently


function toggle_all_tab() {
    document.getElementById("all-mode-button").checked = true;
    let all_tab_els = document.getElementsByClassName("all-tab");
    let group_tab_els = document.getElementsByClassName("group-tab");
    let user_tab_els = document.getElementsByClassName("user-tab");
    for (var i = 0; i < all_tab_els.length; i++) {
        all_tab_els[i].style.display = "";
    }
    for (var i = 0; i < group_tab_els.length; i++) {
        group_tab_els[i].style.display = "none";
    }
    for (var i = 0; i < user_tab_els.length; i++) {
        user_tab_els[i].style.display = "none";
    }
}


function toggle_group_tab(group=null) {
    document.getElementById("group-mode-button").checked = true;
    let all_tab_els = document.getElementsByClassName("all-tab");
    let group_tab_els = document.getElementsByClassName("group-tab");
    let user_tab_els = document.getElementsByClassName("user-tab");
    for (var i = 0; i < all_tab_els.length; i++) {
        all_tab_els[i].style.display = "none";
    }
    for (var i = 0; i < group_tab_els.length; i++) {
        group_tab_els[i].style.display = "";
    }
    for (var i = 0; i < user_tab_els.length; i++) {
        user_tab_els[i].style.display = "none";
    }
}


function toggle_user_tab(user=null) {
    document.getElementById("user-mode-button").checked = true;
    let all_tab_els = document.getElementsByClassName("all-tab");
    let group_tab_els = document.getElementsByClassName("group-tab");
    let user_tab_els = document.getElementsByClassName("user-tab");
    for (var i = 0; i < all_tab_els.length; i++) {
        all_tab_els[i].style.display = "none";
    }
    for (var i = 0; i < group_tab_els.length; i++) {
        group_tab_els[i].style.display = "none";
    }
    for (var i = 0; i < user_tab_els.length; i++) {
        user_tab_els[i].style.display = "";
    }
}


function logout() {
    document.cookie = "access_token = ";
    location.href = "login.html";
}


// USER PAGE FUNCTIONS


function subscribe(group) {
    let group_manage_button = document.getElementById(`manage_button_${group}`);
    group_manage_button.onclick = function () {}; // Block input while loading
    fetch(`api/subscribe?access_token=${access_token}&group=${group}`, {method: "POST"})
        .then((response) => {
            if (response.status == 200) {
                group_manage_button.innerHTML = "Unsubscribe";
                group_manage_button.onclick = function () {unsubscribe(group);};
            } else {
                alert("There was an error subscribing. Please contact support.");
            }
        })
}


function unsubscribe(group) {
    let group_manage_button = document.getElementById(`manage_button_${group}`);
    group_manage_button.onclick = function () {}; // Block input while loading
    fetch(`api/unsubscribe?access_token=${access_token}&group=${group}`, {method: "POST"})
        .then((response) => {
            if (response.status == 200) {
                group_manage_button.innerHTML = "Subscribe";
                group_manage_button.onclick = function () {subscribe(group);};
            } else {
                alert("There was an error unsubscribing. Please contact support.");
            }
        })
}



// MOD PAGE FUNCTIONS


// mod tools
function subscribe_user_to_group() {
    let group = document.getElementById("subscribe_user_group").value;
    let name = document.getElementById("subscribe_user_name").value;
    fetch(
        `api/subscribe_user?access_token=${access_token}&user=${name}&group=${group}`,
        {method: "POST"}
    ).then((response) => {
        if (response.status == "200") {
            alert("User has been subscribed to group.");
        } else {
            alert("There was an error subscribing the user. Please try again.");
        }
    });
}


function create_alias() {
    let alias = document.getElementById("create_alias_name").value;
    let group = document.getElementById("create_alias_group").value;
    fetch(
        `api/create_alias?access_token=${access_token}&alias=${alias}&group=${group}`,
        {method: "POST"}
    ).then((response) => {
        if (response.status == "200") {
            alert("Alias created.");
        } else {
            alert("There was an error creating the alias. Please try again.");
        }
    });
}


function validate_group(e) {
    let group = e.value;
    if (!group.match(/^[A-Z0-9-]+$/)) {
        e.classList.add("bad-input");
        return;
    }
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        let subcategories = groups[cat_idx]["subcategories"]
        for (var subcat_idx = 0; subcat_idx < subcategories.length; subcat_idx++) {
            let group_list = subcategories[subcat_idx]["groups"];
            for (var group_idx = 0; group_idx < group_list.length; group_idx++) {
                if (group_list[group_idx][1] == group) {
                    e.classList.remove("bad-input");
                    return;
                }
            }
        }
    }
    e.classList.add("bad-input");
}


function validate_alias(e) {
    let alias = e.value;
    if (!alias.match(/^[A-Z0-9-]+$/)) {
        e.classList.add("bad-input");
    }else{
        e.classList.remove("bad-input");
    }
}


function validate_username(e) {
    let username = e.value;
    if (!username.match(/^[a-zA-Z0-9_-]{1,20}$/)) {
        e.classList.add("bad-input");
    } else {
        e.classList.remove("bad-input");
    }
}


// banner & footer buttons
function discard_changes() {
    groups = JSON.parse(JSON.stringify(old_groups));
    build_group_table(groups);
}


function update_groups() {
    let body = JSON.stringify({"access_token": access_token, "groups": groups});
    document.getElementById("save-prompt").classList.add("loading");
    document.getElementById("discard-prompt").style.display = "none";
    fetch(
        "api/update_groups",
        {method: "POST", headers: {"Content-Type": "application/json"}, body: body}
    ).then((response) => {
        if (response.status != "200") {
            alert("There was an error updating the groups. Please contact support.");
        } else {
            load_page();
        }
    });
}


// category functions
function move_category_up(category) {
    let category_idx;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (groups[cat_idx]["category_name"] == category) {
            category_idx = cat_idx;
        }
    }
    let current = groups[category_idx];
    let above = groups[category_idx-1];
    if (above) {
        groups[category_idx-1] = current;
        groups[category_idx] = above;
        build_group_table(groups);
    }
}


function move_category_down(category) {
    let category_idx;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (groups[cat_idx]["category_name"] == category) {
            category_idx = cat_idx;
        }
    }
    let current = groups[category_idx];
    let below = groups[category_idx + 1];
    if (below) {
        groups[category_idx+1] = current;
        groups[category_idx] = below;
        build_group_table(groups);
    }
}


function add_category() {
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (groups[cat_idx]["category_name"] == null) {
            return
        }
    }
    groups.splice(0, 0, {"category_name": null, "subcategories": []});
    build_group_table(groups)
}


function edit_category_name(e) {
    category = String(e.target.category);
    if (e.target.value == category) {
        e.target.parentElement.classList.remove("bad-input");
        return;
    }
    let category_idx;
    let valid_name = true;
    if (e.target.value.length == 0) {
        valid_name = false;
    }
    if (e.target.value.includes(":")) {
        valid_name = false;
    }
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (String(groups[cat_idx]["category_name"]) == e.target.value) {
            valid_name = false;
            break;
        }
        if (String(groups[cat_idx]["category_name"]) == category) {
            category_idx = cat_idx;
        }
    }
    if (valid_name) {
        groups[category_idx]["category_name"] = e.target.value;
        build_group_table(groups);
    } else {
        e.target.parentElement.classList.add("bad-input");
    }
}


// Subcategory Functions
function move_subcategory_up(category, subcategory) {
    let category_idx;
    let subcategory_idx;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (groups[cat_idx]["category_name"] == category) {
            category_idx = cat_idx;
        }
    }
    let subcategories = groups[category_idx]["subcategories"]
    for (var subcat_idx = 0; subcat_idx < subcategories.length; subcat_idx++) {
        if (subcategories[subcat_idx]["subcategory_name"] == subcategory) {
            subcategory_idx = subcat_idx;
        }
    }
    let current = groups[category_idx]["subcategories"][subcategory_idx]
    if (groups[category_idx]["subcategories"][subcategory_idx-1] == null) {
        if (groups[category_idx-1] == null) {
            // already at top subcategory of top category
            return
        } else {
            // move to next category up
            let above_subcategories = groups[category_idx-1]["subcategories"];
            for (var subcat_idx = 0; subcat_idx < above_subcategories.length; subcat_idx++) {
                let above_subcategory_name = above_subcategories[subcat_idx]["subcategory_name"];
                if (above_subcategory_name == current["subcategory_name"]) {
                    // name conflict with below category
                    return;
                }
            }
            let last_subcat = groups[category_idx-1]["subcategories"].length;
            groups[category_idx]["subcategories"].splice(subcategory_idx, 1);
            groups[category_idx-1]["subcategories"].splice(last_subcat, 0, current);
            build_group_table(groups);
        }
        // move to next subcategory up
    } else {
        let above = groups[category_idx]["subcategories"][subcategory_idx-1]
        groups[category_idx]["subcategories"][subcategory_idx-1]= current;
        groups[category_idx]["subcategories"][subcategory_idx] = above;
        build_group_table(groups);
    }
}


function move_subcategory_down(category, subcategory) {
    let category_idx;
    let subcategory_idx;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (groups[cat_idx]["category_name"] == category) {
            category_idx = cat_idx;
        }
    }
    let subcategories = groups[category_idx]["subcategories"]
    for (var subcat_idx = 0; subcat_idx < subcategories.length; subcat_idx++) {
        if (subcategories[subcat_idx]["subcategory_name"] == subcategory) {
            subcategory_idx = subcat_idx;
        }
    }
    let current = groups[category_idx]["subcategories"][subcategory_idx]
    if (groups[category_idx]["subcategories"][subcategory_idx+1] == null) {
        if (groups[category_idx+1] == null) {
            // already at bottom subcategory of bottom category
            return
        } else {
            // move to next category down
            let below_subcategories = groups[category_idx+1]["subcategories"];
            for (var subcat_idx = 0; subcat_idx < below_subcategories.length; subcat_idx++) {
                let below_subcategory_name = below_subcategories[subcat_idx]["subcategory_name"];
                if (below_subcategory_name == current["subcategory_name"]) {
                    // name conflict with below category
                    return;
                }
            }
            groups[category_idx]["subcategories"].splice(subcategory_idx, 1);
            groups[category_idx+1]["subcategories"].splice(0, 0, current);
            build_group_table(groups);
        }
        // move to next subcategory
    } else {
        let below = groups[category_idx]["subcategories"][subcategory_idx+1]
        groups[category_idx]["subcategories"][subcategory_idx+1]= current;
        groups[category_idx]["subcategories"][subcategory_idx] = below;
        build_group_table(groups);
    }
}


function add_subcategory(category) {
    let category_idx;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (groups[cat_idx]["category_name"] == category) {
            category_idx = cat_idx;
        }
    }
    for (var subcat_idx = 0; subcat_idx < groups[category_idx]["subcategories"].length; subcat_idx++) {
        if (groups[category_idx]["subcategories"][subcat_idx]["subcategory_name"] == null)
            // Don't add a new subcategory if there's already an unnamed one
            return;
    }
    groups[category_idx]["subcategories"].splice(0, 0, {"subcategory_name": null, "groups": []});
    build_group_table(groups);
}


function edit_subcategory_name(e) {
    category = String(e.target.category);
    subcategory = String(e.target.subcategory);
    if (e.target.value == subcategory) {
        e.target.parentElement.classList.remove("bad-input");
        return;
    }
    let valid_name = true;
    if (e.target.value.includes(":")) {
        valid_name = false;
    }
    let category_idx;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (String(groups[cat_idx]["category_name"]) == category) {
            category_idx = cat_idx;
        }
    }
    let subcategory_idx;
    for (var subcat_idx = 0; subcat_idx < groups[category_idx]["subcategories"].length; subcat_idx++) {
        let alsocheck = e.target.value;
        if (e.target.value == "") {
            alsocheck = "null";
        }
        if (
            (String(groups[category_idx]["subcategories"][subcat_idx]["subcategory_name"]) == e.target.value)
            || (String(groups[category_idx]["subcategories"][subcat_idx]["subcategory_name"]) == alsocheck)
        ) {
            valid_name = false;
            break;
        }
        if (String(groups[category_idx]["subcategories"][subcat_idx]["subcategory_name"]) == subcategory) {
            subcategory_idx = subcat_idx;
        }
    }
    if (valid_name) {
        let target = e.target.value;
        if (target == "") {
            target = null;
        }
        groups[category_idx]["subcategories"][subcategory_idx]["subcategory_name"] = target;
        build_group_table(groups);
    } else {
        e.target.parentElement.classList.add("bad-input");
    }
}


// group functions
function move_group_up(group_id) {
    let category_index;
    let subcategory_index;
    let group_index;
    let group;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        let subcategories = groups[cat_idx]["subcategories"]
        for (var subcat_idx = 0; subcat_idx < subcategories.length; subcat_idx++) {
            let group_list = subcategories[subcat_idx]["groups"]
            for (var group_idx = 0; group_idx < group_list.length; group_idx++) {
                if (group_list[group_idx][7] == group_id) {
                    category_index = cat_idx;
                    subcategory_index = subcat_idx;
                    group_index = group_idx;
                    group = group_list[group_idx];
                }
            }
        }
    }
    if (groups[category_index]["subcategories"][subcategory_index-1] == null) {
        if (groups[category_index-1] == null) {
            // already in top subcategory of top category
            return;
        } else {
            // move to next category up
            let last_subcat = groups[category_index-1]["subcategories"].length-1;
            groups[category_index]["subcategories"][subcategory_index]["groups"].splice(group_index, 1);
            groups[category_index-1]["subcategories"][last_subcat]["groups"].splice(0, 0, group);
            build_group_table(groups);
        }
    } else {
        // move to next subcategory up
        groups[category_index]["subcategories"][subcategory_index]["groups"].splice(group_index, 1);
        groups[category_index]["subcategories"][subcategory_index-1]["groups"].splice(0, 0, group);
        build_group_table(groups);
    }
}


function move_group_down(group_id) {
    let category_index;
    let subcategory_index;
    let group_index;
    let group;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        let subcategories = groups[cat_idx]["subcategories"]
        for (var subcat_idx = 0; subcat_idx < subcategories.length; subcat_idx++) {
            let group_list = subcategories[subcat_idx]["groups"]
            for (var group_idx = 0; group_idx < group_list.length; group_idx++) {
                if (group_list[group_idx][7] == group_id) {
                    category_index = cat_idx;
                    subcategory_index = subcat_idx;
                    group_index = group_idx;
                    group = group_list[group_idx];
                }
            }
        }
    }
    if (groups[category_index]["subcategories"][subcategory_index+1] == null) {
        if (groups[category_index+1] == null) {
            // already in bottom subcategory of bottom group
            return;
        } else {
            // move to next category down
            groups[category_index]["subcategories"][subcategory_index]["groups"].splice(group_index, 1);
            groups[category_index+1]["subcategories"][0]["groups"].splice(0, 0, group);
            build_group_table(groups);
        }
    } else {
        // pop to next subcategory down
        groups[category_index]["subcategories"][subcategory_index]["groups"].splice(group_index, 1);
        groups[category_index]["subcategories"][subcategory_index+1]["groups"].splice(0, 0, group);
        build_group_table(groups);
    }
}


function add_group(category, subcategory) {
    let category_idx;
    let subcategory_idx;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        if (groups[cat_idx]["category_name"] == category) {
            category_idx = cat_idx;
        }
    }
    for (var subcat_idx = 0; subcat_idx < groups[category_idx]["subcategories"].length; subcat_idx++) {
        if (groups[category_idx]["subcategories"][subcat_idx]["subcategory_name"] == subcategory) {
            subcategory_idx = subcat_idx;
        }
    }
    for (var group_idx = 0; group_idx < groups[category_idx]["subcategories"][subcategory_idx]["groups"].length; group_idx++) {
        if (groups[category_idx]["subcategories"][subcategory_idx]["groups"][group_idx][1] == "") {
            return
        }
    }
    let group_ids = [];
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        for (var subcat_idx = 0; subcat_idx < groups[cat_idx]["subcategories"].length; subcat_idx++) {
            for (var group_idx = 0; group_idx < groups[cat_idx]["subcategories"][subcat_idx]["groups"].length; group_idx++) {
                group_ids.push(groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][7]);
            }
        }
    }
    new_group_id = Math.max(...group_ids) + 1;
    let new_group = [0, "", "", 0, 0, 0, 0, new_group_id];
    groups[category_idx]["subcategories"][subcategory_idx]["groups"].splice(0, 0, new_group);
    build_group_table(groups);
}


function edit_group_name(e) {
    let group_id = e.target.group_id;
    let old_name = e.target.group_name;
    let new_name = e.target.value;
    valid_name = true;
    if (old_name == new_name) {
        e.target.parentElement.classList.remove("bad-input");
        return
    }
    if ( !new_name.match(/^[A-Z0-9-]+$/) ) {
        valid_name = false;
    }
    let category_index;
    let subcategory_index;
    let group_index;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        for (var subcat_idx = 0; subcat_idx < groups[cat_idx]["subcategories"].length; subcat_idx++) {
            for (var group_idx = 0; group_idx < groups[cat_idx]["subcategories"][subcat_idx]["groups"].length; group_idx++) {
                if (groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][1] == new_name) {
                    valid_name = false;
                    break;
                }
                if (groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][7] == group_id) {
                    category_index = cat_idx;
                    subcategory_index = subcat_idx;
                    group_index = group_idx;
                }
            }
        }
    }
    if (valid_name) {
        groups[category_index]["subcategories"][subcategory_index]["groups"][group_index][1] = new_name;
        build_group_table(groups);
    } else {
        e.target.parentElement.classList.add("bad-input");
    }
}


function edit_group_description(e) {
    let group_id = e.target.group_id;
    let old_description = e.target.group_description;
    let new_description = e.target.value;
    if (old_description == new_description) {
        e.target.parentElement.classList.remove("bad-input");
        return
    }
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        for (var subcat_idx = 0; subcat_idx < groups[cat_idx]["subcategories"].length; subcat_idx++) {
            for (var group_idx = 0; group_idx < groups[cat_idx]["subcategories"][subcat_idx]["groups"].length; group_idx++) {
                if (groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][7] == group_id) {
                    groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][2] = new_description;
                }
            }
        }
    }
    build_group_table(groups);
}

function edit_group_protected (e) {
    let group_id = e.target.group_id;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        for (var subcat_idx = 0; subcat_idx < groups[cat_idx]["subcategories"].length; subcat_idx++) {
            for (var group_idx = 0; group_idx < groups[cat_idx]["subcategories"][subcat_idx]["groups"].length; group_idx++) {
                if (groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][7] == group_id) {
                    groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][3] = e.target.checked ? 1 : 0;
                }
            }
        }
    }
    build_group_table(groups);
}

function edit_group_locked (e) {
    let group_id = e.target.group_id;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        for (var subcat_idx = 0; subcat_idx < groups[cat_idx]["subcategories"].length; subcat_idx++) {
            for (var group_idx = 0; group_idx < groups[cat_idx]["subcategories"][subcat_idx]["groups"].length; group_idx++) {
                if (groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][7] == group_id) {
                    groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][6] = e.target.checked ? 1 : 0;
                }
            }
        }
    }
    build_group_table(groups);
}

function edit_group_hidden (e) {
    let group_id = e.target.group_id;
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        for (var subcat_idx = 0; subcat_idx < groups[cat_idx]["subcategories"].length; subcat_idx++) {
            for (var group_idx = 0; group_idx < groups[cat_idx]["subcategories"][subcat_idx]["groups"].length; group_idx++) {
                if (groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][7] == group_id) {
                    groups[cat_idx]["subcategories"][subcat_idx]["groups"][group_idx][5] = e.target.checked ? 1 : 0;
                }
            }
        }
    }
    build_group_table(groups);
}


// TODO clean up this mess


function build_group_table(groups) {

    // If groups have been edited prompt to save
    let save_prompt = document.getElementById("save-prompt");
    let discard_prompt = document.getElementById("discard-prompt");
    if (JSON.stringify(groups) != JSON.stringify(old_groups)) {
        save_prompt.style.display = "";
        discard_prompt.style.display = "";
        document.getElementById("toggle-mod-mode").classList.add("bad-input");
    } else {
        save_prompt.style.display = "none";
        discard_prompt.style.display = "none";
        document.getElementById("toggle-mod-mode").classList.remove("bad-input");
    }

    // Create the "Ping Groups:" header
    document.getElementById("groups").innerHTML = "";
    const groups_header = document.createElement("h1");
    groups_header_text = document.createTextNode("Ping Groups ");
    groups_header.appendChild(groups_header_text);
    if (mod_mode) {
        let create_category_button = document.createElement("button");
        document.getElementById("groups").classList.remove("user-mode");
        create_category_button.style.verticalAlign = "middle";
        create_category_button.addEventListener("click", add_category);
        create_category_button.appendChild(document.createTextNode("\u{2795}"));
        groups_header.appendChild(create_category_button);
    } else {
        document.getElementById("groups").classList.add("user-mode");
    }
    document.getElementById("groups").appendChild(groups_header);

    // Iterate over groups to build table
    for (var cat_idx = 0; cat_idx < groups.length; cat_idx++) {
        let category = groups[cat_idx];
        let category_name = category["category_name"];

        // Create category if it doesn't exist
        if (document.getElementById(`groups_${category_name}`) == null) {
            const category_element = document.createElement("div");
            category_element.classList.add("group-category");
            const category_title = document.createElement("h2");
            if (mod_mode) {
                category_move_up = document.createElement("button");
                category_move_up.appendChild(document.createTextNode("\u{2B06}"));
                category_move_up.addEventListener("click", function() {move_category_up(category_name);});
                category_title.appendChild(category_move_up);
                category_move_down = document.createElement("button");
                category_move_down.addEventListener("click", function() {move_category_down(category_name);});
                category_move_down.appendChild(document.createTextNode("\u{2B07}"));
                category_title.appendChild(category_move_down);
                category_text = document.createElement("Input");
                category_text.category = category_name;
                category_text.onchange = edit_category_name;
                category_text.value = category_name;
                category_title.appendChild(category_text)
                create_subcategory = document.createElement("button");
                create_subcategory.addEventListener("click", function() {add_subcategory(category_name);});
                create_subcategory.appendChild(document.createTextNode("\u{2795}"));
                category_title.appendChild(create_subcategory);
            } else {
                category_text = document.createTextNode(category_name+" ");
                category_title.appendChild(category_text)
            }
            category_element.appendChild(category_title);
            category_element.id = `groups_${category_name}`
            document.getElementById("groups").appendChild(category_element);
        }

        // Iterate over subcategories
        for(var subcat_idx = 0; subcat_idx < category["subcategories"].length; subcat_idx++) {
            let subcategory = category["subcategories"][subcat_idx];
            let subcategory_name = subcategory["subcategory_name"];

            // Some categories do not have subcategories. These are indicated with "null"
            // Create the subcategory element here. Append it below IFF not already exists
            const subcategory_element = document.createElement("div");
            subcategory_element.classList.add("group-subcategory");
            if (subcategory_name || mod_mode) {
                const subcategory_title = document.createElement("h3");
                if (mod_mode) {
                    subcategory_move_up = document.createElement("button");
                    subcategory_move_up.addEventListener(
                        "click", function() {move_subcategory_up(category_name, subcategory_name);}
                    );
                    subcategory_move_up.appendChild(document.createTextNode("\u{2B06}"));
                    subcategory_title.appendChild(subcategory_move_up);
                    subcategory_move_down = document.createElement("button");
                    subcategory_move_down.addEventListener(
                        "click", function() {move_subcategory_down(category_name, subcategory_name);}
                    );
                    subcategory_move_down.appendChild(document.createTextNode("\u{2B07}"));
                    subcategory_title.appendChild(subcategory_move_down);
                    subcategory_text = document.createElement("Input");
                    subcategory_text.category = category_name;
                    subcategory_text.subcategory = subcategory_name;
                    subcategory_text.onchange = edit_subcategory_name;
                    subcategory_text.value = subcategory_name;
                    subcategory_title.appendChild(subcategory_text);
                    create_group = document.createElement("button");
                    create_group.addEventListener(
                        "click", function() {add_group(category_name, subcategory_name);}
                    );
                    create_group.appendChild(document.createTextNode("\u{2795}"));
                    subcategory_title.appendChild(create_group);
                } else {
                    subcategory_text = document.createTextNode(subcategory_name);
                    subcategory_title.appendChild(subcategory_text);
                }
                subcategory_element.appendChild(subcategory_title);
            }
            subcategory_element.id = `groups_${category_name}_${subcategory_name}`
            subcategory_element.classList.add("subcategory");

            // Create subcategory if it doesn't exist. Get it if it does.
            if (document.getElementById(`groups_${category_name}_${subcategory_name}_table`) == null) {
                subcategory_table = document.createElement("table")
                subcategory_table.id = `groups_${category_name}_${subcategory_name}_table`;
                document.getElementById(`groups_${category_name}`).append(subcategory_element);
                document.getElementById(subcategory_element.id).append(subcategory_table);
            } else {
                subcategory_table = document.getElementById(`groups_${category_name}_${subcategory_name}_table`);
            }

            // Create table header if not exists
            let columns;
            if (mod_mode) {
                columns = ["", "", "Name", "Description", "\u{270B}", "\u{1F512}", "\u{1F648}"];
            } else {
                columns = ["", "Name", "Description", "\u{1F4E9}"];
            }
            if (document.getElementById(`groups_${category_name}_${subcategory_name}_th`) == null) {
                let subcategory_header = document.createElement("tr");
                subcategory_header.id = `groups_${category_name}_${subcategory_name}_th`
                for (var col_idx = 0; col_idx < columns.length; col_idx++) {
                    let cell_element = document.createElement("th");
                    column_element = document.createTextNode(columns[col_idx]);
                    cell_element.appendChild(column_element);
                    subcategory_header.appendChild(cell_element);
                }
                if (subcategory["groups"].length > 0) {
                    document.getElementById(subcategory_table.id).append(subcategory_header);
                }
            }

            // Create rows in subcategory for each group
            for (var group_idx = 0; group_idx < subcategory["groups"].length; group_idx++) {
                group_element = document.getElementById(subcategory_table.id).insertRow();
                let group = subcategory["groups"][group_idx];
                let group_subscribed = group[0];
                let group_protected = group[3];
                let group_hidden = group[5];
                let group_locked = group[6];
                const group_manage = document.createElement("button")
                group_manage.id = `manage_button_${group[1]}`;
                if (group_subscribed) {
                    group_manage.appendChild(document.createTextNode("Unsubscribe"))
                    group_manage.onclick = function () {unsubscribe(group[1]);};
                } else {
                    if (group_protected) {
                        if (!mod_mode) {
                            group_manage.classList.add("bad-input");
                            group_manage.appendChild(document.createTextNode("Protected"));
                        } else {
                            group_manage.appendChild(document.createTextNode("Subscribe"));
                            group_manage.onclick = function () {subscribe(group[1]);};
                        }
                    } else {
                        group_manage.appendChild(document.createTextNode("Subscribe"));
                        group_manage.onclick = function () {subscribe(group[1]);};
                    }
                }
                let group_name;
                let group_description;
                if (mod_mode) {
                    group_name = document.createElement("Input");
                    group_name.value = group[1];
                    group_name.group_id = group[7];
                    group_name.group_name = group[1];
                    group_name.onchange = edit_group_name;
                    group_description = document.createElement("Input");
                    group_description.value = group[2]
                    group_description.group_id = group[7];
                    group_description.group_description = group[2];
                    group_description.onchange = edit_group_description;
                } else {
                    group_name = document.createTextNode(group[1]);
                    group_description = document.createTextNode(group[2]);
                }
                let group_activity = document.createTextNode(group[4]);
                let group_move_up = document.createElement("button");
                group_move_up.addEventListener("click", function() {move_group_up(group[7]);});
                group_move_up.appendChild(document.createTextNode("\u{2B06}"));
                let group_move_down = document.createElement("button");
                group_move_down.addEventListener("click", function() {move_group_down(group[7]);});
                group_move_down.appendChild(document.createTextNode("\u{2B07}"));
                let group_protected_element = document.createElement("input");
                group_protected_element.type = "checkbox";
                group_protected_element.checked = group_protected;
                group_protected_element.group_id = group[7];
                group_protected_element.addEventListener("click", edit_group_protected);
                let group_hidden_element = document.createElement("input");
                group_hidden_element.type = "checkbox";
                group_hidden_element.checked = group_hidden;
                group_hidden_element.group_id = group[7];
                group_hidden_element.addEventListener("click", edit_group_hidden);
                let group_locked_element = document.createElement("input");
                group_locked_element.type = "checkbox";
                group_locked_element.checked = group_locked;
                group_locked_element.group_id = group[7];
                group_locked_element.addEventListener("click", edit_group_locked);

                let cells;
                if (mod_mode) {
                    cells = [
                        group_move_up,
                        group_move_down,
                        group_name,
                        group_description,
                        group_protected_element,
                        group_locked_element,
                        group_hidden_element,
                    ];
                } else {
                    cells = [
                        group_manage,
                        group_name,
                        group_description,
                        group_activity,
                    ];
                }
                for (var cell_idx = 0; cell_idx < cells.length; cell_idx++) {
                    let cell_element = group_element.insertCell();
                    cell_element.appendChild(cells[cell_idx]);
                    group_element.appendChild(cell_element);
                }
            }
        }
    }
}
