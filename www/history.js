// There's apparently no way to default to today's date in pure html
//
// I really hate webdev

document.getElementById("search-date").valueAsDate = new Date();

function search_ping_log() {
    let group_name = document.getElementById("search-group-name").value.toUpperCase();
    let epoch_sec = document.getElementById("search-date").valueAsNumber / 1000;
    let sort;
    let selected_sort = document.querySelector('input[name="search_type"]:checked').id
    if (selected_sort == "search-before") {
        sort = "DESC";
    } else {
        sort = "ASC";
    }
    let count = document.getElementById("search-count").value;
    
    fetch(
        `api/get_ping_log?group_name=${group_name}&sort=${sort}&epoch_sec=${epoch_sec}&count=${count}`
    ).then((response) => {
        if (response.status != "200") {
            alert("something went wrong, try again")
        }
        return response.json()
    }).then((data) => {
        const results = document.createElement("ul");
        for (var idx = 0; idx < data.length; idx++) {
            let comment_element = document.createElement("li");
            let link_element = document.createElement("a");
            let link_date = new Date(0);
            link_date.setUTCSeconds(data[idx][0]);
            link_element.href = `https://reddit.com${data[idx][2]}`;
            let link_label = document.createTextNode(link_date.toLocaleString());
            link_element.appendChild(link_label);
            comment_element.appendChild(link_element)
            results.appendChild(comment_element);
        }
        document.getElementById("search-results").innerHTML = "";
        document.getElementById("search-results").appendChild(results);
    });
}
