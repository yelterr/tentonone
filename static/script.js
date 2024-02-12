// Starts the rating from a button
function startGame() {
    updateGenderChoice();
    fetch('/rate')
        .then(response => {
            if (response.ok) {
                // If the response is successful, navigate to the new page
                window.location.href = '/rate';
            } else {
                console.error('Failed to invoke Python function');
            }
        })
        .catch(error => {
            console.error('Error invoking Python function:', error);
    });
}

// Changes the image (game.html)
function loadImage() {
    fetch('/get_image')
        .then(response => response.json())
        .then(data => {
            const url = data.result.impath;
            const name = data.result.name;

            // Set the image source dynamically
            document.getElementById('loadedImage').src = url;
            document.getElementById('name-overlay').innerText = name;
            document.getElementById("name-bottom").innerText = name
            document.getElementById("name_result").innerText = name
        });
}

// Handles the "next" page when a user submits.
function showAndRemoveNext() {
    var button = document.getElementById("gameButton");
    var submit_div = document.getElementById("submit_div");
    var results_div = document.getElementById("results_div");

    var slider = document.getElementById("rating_slider");
    var textInput = document.getElementById("textInput");

    // Changes Button Text
    if (button.innerText.slice(0, 6) === "Submit") {
        makeNext();
    } else {
        makeSubmit();
    }
}

function makeSubmit() {
    var button = document.getElementById("gameButton")
    var leaderboard_button = document.getElementById("leaderboard-button");
    
    // var submit_div = document.getElementById("submit_div")
    // var results_div = document.getElementById("results_div")

    var submit_to_reveal = document.getElementById("submit-to-reveal");
    var revealed = document.getElementById("revealed");

    var slider = document.getElementById("rating_slider");
    var textInput = document.getElementById("textInput");
    
    updateGenderChoice();
    loadImage();
    button.innerHTML = "Submit <span id='final-number'></span>/10"
    slider.value = 5
    textInput.value = 5

    revealed.style.display = "none"
    submit_to_reveal.style.display = "block"
    
    leaderboard_button.style.display = "none"

    slider.disabled = false;
    textInput.disabled = false;
    document.getElementById("final-number").innerText = slider.value;
}


function makeNext() {
    sendRating();

    var button = document.getElementById("gameButton");
    var leaderboard_button = document.getElementById("leaderboard-button");

    // var submit_div = document.getElementById("submit_div")
    // var results_div = document.getElementById("results_div")

    var submit_to_reveal = document.getElementById("submit-to-reveal");
    var revealed = document.getElementById("revealed");

    var slider = document.getElementById("rating_slider");
    var textInput = document.getElementById("textInput");

    button.innerText = "Next"

    submit_to_reveal.style.display = "none"
    revealed.style.display = "block"

    leaderboard_button.style.display = "block"

    slider.disabled = true;
    textInput.disabled = true;
}

// Sends the value of the slider and image path to backend.py (game.html)
function sendRating() {
    var imagePath = document.getElementById("loadedImage").src;
    var sliderValue = document.getElementById("rating_slider").value;
    var genderChoice = localStorage.getItem("selectedOption");

    var avg_rating_txt = document.getElementById("avg_rating")
    var amt_raters_txt = document.getElementById("amt_raters")
    var ranking_txt = document.getElementById("ranking")

    // Make an AJAX request to send the slider value to the server
    fetch('/send_rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'slider_value': sliderValue, "image_path": imagePath }),
    })
    .then(response => response.json())
    .then(data => {
        // Changes the avg_rating text to the actual average rating
        const rating = data.result.rating
        const amt_raters = data.result.amt_raters
        const ranking = data.result.ranking

        avg_rating_txt.innerText = rating
        amt_raters_txt.innerText = amt_raters
        ranking_txt.innerText = "#" + ranking
    });

}

// Keeps the dropdown consistent between pages
function saveSelectedOption() {
    var dropdown = document.getElementById("myDropdown");
    var selectedValue = dropdown.value;

    const choices = ["both", "men", "women"]
    if (!choices.includes(selectedValue)) {
        selectedValue = "both";
    }

    localStorage.setItem("selectedOption", selectedValue);
}

window.onload = function () {
    var currentPath = window.location.pathname;
    if (currentPath == "/leaderboard") {
        makeFilterDropdownChanges();
    }

    var dropdown = document.getElementById("myDropdown");
    var selectedValue = localStorage.getItem("selectedOption")
    const choices = ["both", "men", "women"]

    if (!selectedValue || !choices.includes(selectedValue)) {
        selectedValue = "both";
        localStorage.setItem("selectedOption", selectedValue);
        updateGenderChoice();
    }

    dropdown.value = selectedValue;
}

function updateGenderChoice() {
    var genderChoice = localStorage.getItem("selectedOption");

    const choices = ["both", "men", "women"]
    if (!choices.includes(genderChoice)) {
        genderChoice = "both";
        localStorage.setItem("selectedOption", genderChoice);
    }

    fetch('/update_gender_choice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'gender_choice':  genderChoice}),
    });
}

// Whenever the gender dropdown changes, make changes depending on the page
function makeGenderDropdownChanges() {
    saveSelectedOption();
    updateGenderChoice();
    // #1: Check what page I am on to decide what I have to update.
    // #2: If Main Menu, continue.
    // #3: If Rating Page, then check if image does not match with gender choice. If it does, continue. If it doesn't, change it.
    // #4: If Leaderboard, change the leaderboard.
    var dropdownValue = document.getElementById("myDropdown").value;
    var currentPath = window.location.pathname;

    // If we are in game
    if (currentPath == "/rate") {
        var impath = document.getElementById("loadedImage").src
    
        // Check if an image change is needed
        if (dropdownValue == "both") {
            ;
        }
        else if (dropdownValue == "women") {
            if (!(impath.includes("/women"))) {
                //loadImage();
                makeSubmit();
            }
        }
        else if (dropdownValue == "men") {
            if (!(impath.includes("/men"))) {
                //loadImage();
                makeSubmit();
            }
        }
    }
    // If we are in main menu
    else if (currentPath == "/") {
        ;
    }
    // If we are in leaderboard
    else if (currentPath == "/leaderboard") {
        makeFilterDropdownChanges();
    }

    saveSelectedOption();
}

function makeFilterDropdownChanges() {
    updateGenderChoice();

    var filterChoice = document.getElementById("filterDropdown").value;
    var genderChoice = localStorage.getItem("selectedOption");

    
    // NEW LEADERBOARD POPULATION
    var leaderboard = document.getElementById("leaderboard-background")
    var children = leaderboard.children;
    var childrenArray = Array.from(children);
    childrenArray.forEach(function(child) {
        leaderboard.removeChild(child);
    });

    fetch('/retrieve_ratings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'filterChoice': filterChoice, "genderChoice": genderChoice}),
    })
    .then(response => response.json())
    .then(data => {
        // I need POSITION, NAME, RATING, AMT_RATERS, IMPATH
        const rankings = data.result

        // (margaret_thatcher.jpg, 38, 7.99211, 1, Joao Pereira)
        for (let i = 0, len = rankings.length; i < len; i++) {
            var impath = rankings[i][0];
            var amt_raters = rankings[i][1]
            var rating = rankings[i][2]
            var position = rankings[i][3]
            var name = rankings[i][4]

            const leaderboard_item = document.createElement("div");
            leaderboard_item.className = "leaderboard-element"
            leaderboard_item.innerHTML = `
            <div class="position-div">
                    <p class="position-txt">${position}</p>
                </div>

                <div class="not-position-div">
                    <img class="leaderboard-img" src="${impath}">

                    <div class="name-and-raters">
                        <p class="name-txt" style="margin: 0; padding: 0;">${name}</p>
                        <p style="margin: 0; padding: 0; font-size: 13px;">rated by ${amt_raters} people</p>
                    </div>

                    <div class="rating-div">
                        <div class="has-the-numbers">
                            <p class="number-txt" style="margin: 0; padding: 0;">${rating}</p>
                            <p class="out-of-ten" style="margin-top: 3px; padding: 0;">/10</p>
                        </div>
                    </div>

                </div>
                `

            leaderboard.appendChild(leaderboard_item)
        }

        // Filtering the new leaderboard elements for anything already in the search bar
        const searchTerm = searchInput.value.toLowerCase();
        const elements = document.getElementsByClassName('leaderboard-element');

        for (let i = 0; i < elements.length; i++) {
            const elementText = elements[i].textContent.toLowerCase();

            // Hide or show elements based on the search term
            if (elementText.includes(searchTerm)) {
                elements[i].style.display = 'flex';
            } else {
                elements[i].style.display = 'none';
            }
        }

    });



}