// Apparently the best way to set a datetime-local object to the current
// date and time in Javascript involves taking a date object, undoing the
// GMT offset, converting it to a string, SLICING THAT STRING, and then
// setting THAT as the value of the datetime-local object
//
// I am losing my goddamn mind over here. Am I the stupid one or is this
// actually fucking insane? Am I in a nightmare right now? Am I in hell?


document.getElementById("search-group-name").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        search_ping_log();
    }
});
reset_date();
params = new URLSearchParams(window.location.search);
// stupid logic, don't care
if (params.size === 1) {
    document.getElementById("search-group-name").value = params.get("group_name").toUpperCase();
    search_ping_log();
} else if (params.size === 2) {
    document.getElementById("search-count").value = params.get("count");
    document.getElementById("search-group-name").value = params.get("group_name").toUpperCase();
    search_ping_log();
} else if (params.size > 1) {
    document.getElementById("search-group-name").value = params.get("group_name").toUpperCase();
    document.getElementById("search-count").value = params.get("count");
    let epoch = new Date(params.get("epoch_sec") * 1000);
    epoch.setMinutes(epoch.getMinutes() - epoch.getTimezoneOffset());
    document.getElementById('search-date').value = epoch.toISOString().slice(0,19)
    if (params.get("sort") === "ASC") {
        document.getElementById("search-after").checked = true;
    }
}
search_ping_log();


function reset_date() {
    let now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('search-date').value = now.toISOString().slice(0,19)
}


function get_selected_sort() {
    selected_sort = document.querySelector('input[name="search_type"]:checked').id;
    if (selected_sort == "search-before") {
        return "DESC";
    }
    return "ASC";
}


function search_ping_log() {
    let group_name = document.getElementById("search-group-name").value.toUpperCase();
    let search_date = new Date(document.getElementById("search-date").value);
    let epoch_sec = Math.floor(search_date.getTime() / 1000);
    let sort;
    sort = get_selected_sort();
    let count = document.getElementById("search-count").value;
    params = `?group_name=${group_name}&epoch_sec=${epoch_sec}&sort=${sort}&count=${count}`;
    history.pushState({}, "", `${window.location.origin}${window.location.pathname}${params}`);

    fetch(
        `api/get_ping_log?group_name=${group_name}&sort=${sort}&epoch_sec=${epoch_sec}&count=${count}`
    ).then((response) => {
        if (response.status != "200") {
            alert("Group not found. Please try again.")
        }
        return response.json()
    }).then((data) => {
        if (data.length === 0) {
            document.getElementById("search-results").innerHTML = "No results found - try a different search";
            return;
        }
        const results = document.createElement("div");
        results.id = "search-results-list";
        results.setAttribute("search-group-name", group_name);
        results.setAttribute("search-count", count);
        const script = document.createElement("script");
        script.charset = "UTF-8";
        for (var idx = 0; idx < data.length; idx++) {
            let created_utc = data[idx][0];
            let result_element = document.createElement("div");
            result_element.classList.add("search-result");
            result_element.setAttribute("created_utc", created_utc);
            let date_element = document.createElement("div");
            let date = new Date(data[idx][0]*1000 ).toLocaleString();
            let date_text = document.createTextNode(date);
            date_element.appendChild(date_text);
            let comment_element = document.createElement("blockquote");
            comment_element.setAttribute("class", "reddit-embed-bq");
            comment_element.setAttribute("data-embed-locale","en-EN");
            comment_element.setAttribute("data-embed-context","1");
            comment_element.setAttribute("data-embed-depth","2");
            comment_element.setAttribute("data-embed-height","340");
            let link_element = document.createElement("a");
            link_element.href = `https://reddit.com${data[idx][2]}`;
            comment_element.appendChild(link_element);
            result_element.appendChild(date_element);
            result_element.appendChild(comment_element);
            results.appendChild(result_element);
        }
        document.getElementById("search-results").innerHTML = "";
        document.getElementById("search-results").appendChild(results);
        // I can't tell if I'm completely misunderstanding how JS is meant to be used or
        // if it's really just this unweildy. I _want_ to just create the pagination object
        // once and then duplicate it, but there's no way to do that while preserving event
        // listeners... which is kinda important for buttons
        pagination_top = document.createElement("span");
        pagination_bottom = document.createElement("span");
        previous_button_top = document.createElement("button");
        previous_button_bottom = document.createElement("button");
        previous_button_top.appendChild(document.createTextNode("Older"));
        previous_button_bottom.appendChild(document.createTextNode("Older"));
        previous_button_top.addEventListener("click", load_previous);
        previous_button_bottom.addEventListener("click", load_previous);
        next_button_top = document.createElement("button");
        next_button_bottom = document.createElement("button");
        next_button_top.appendChild(document.createTextNode("Newer"));
        next_button_bottom.appendChild(document.createTextNode("Newer"));
        next_button_top.addEventListener("click", load_next);
        next_button_bottom.addEventListener("click", load_next);
        pagination_top.appendChild(previous_button_top);
        pagination_bottom.appendChild(previous_button_bottom);
        pagination_top.appendChild(next_button_top);
        pagination_bottom.appendChild(next_button_bottom);
        document.getElementById("search-results").prepend(pagination_top);
        document.getElementById("search-results").append(pagination_bottom);
        load_embeds();
    });
}


function load_previous() {
    results_container = document.getElementById("search-results-list");
    group_name = results_container.getAttribute("search-group-name");
    epoch_sec = results_container.lastChild.getAttribute("created_utc");
    count = results_container.getAttribute("search-count");
    sort = get_selected_sort();
    params = `?group_name=${group_name}&epoch_sec=${epoch_sec}&sort=DESC&count=${count}`
    window.location.replace(`${window.location.origin}${window.location.pathname}${params}`)
}


function load_next() {
    results_container = document.getElementById("search-results-list");
    group_name = results_container.getAttribute("search-group-name");
    epoch_sec = results_container.lastChild.getAttribute("created_utc");
    count = results_container.getAttribute("search-count");
    sort = get_selected_sort();
    params = `?group_name=${group_name}&epoch_sec=${epoch_sec}&sort=ASC&count=${count}`
    window.location.replace(`${window.location.origin}${window.location.pathname}${params}`)
}
