jQuery(document).ready(function ($) {
    function fetchTopUsers() {
        $.ajax({
            url: topUsersAjax.ajaxurl,
            method: 'POST',
            data: {
                action: 'fetch_top_users'
            },
            success: function (response) {
                console.log(response);
                if (response.success) {
                    // Save JSON object array to local storage as a string
                    localStorage.setItem('topUsersData', JSON.stringify(response.data));
                    renderTopUsers(response.data); // Render the table from the response
                } else {
                    $('#top-users-container').html('<p>' + response.data + '</p>');
                }
            },
            error: function () {
                $('#top-users-container').html('<p>Error fetching data.</p>');
            }
        });
    }

    // Function to render JSON objects in the table format
    function renderTopUsers(topUsers) {
        var i = 1;
        topUsers.forEach(user => {
            const userDataRank = document.getElementById("user" + i + "rank");
            const userDataName = document.getElementById("user" + i + "name");
            const userDataPoints = document.getElementById("user" + i + "points");
            if (userDataName !== null) {
                userDataName.innerHTML = user.name;
            }
            if (userDataPoints !== null) {
                userDataPoints.innerHTML = user.points;
            }
            if (userDataRank !== null) {
                userDataRank.innerHTML = user.rank;
            }
            console.log(i);
            console.log(user);
            i++;
        });
    }

    // On initial load, render from local storage


    // Fetch new data every 1 seconds
    setInterval(fetchTopUsers, 1000);


});
