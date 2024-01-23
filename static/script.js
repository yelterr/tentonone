// Starts the rating from a button
function startGame() {
    updateGenderChoice();
    fetch('/game')
        .then(response => {
            if (response.ok) {
                // If the response is successful, navigate to the new page
                window.location.href = '/game';
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
        });
}

// Handles the "next" page when a user submits.
function showAndRemoveNext() {
    var button = document.getElementById("gameButton")
    var avg_rating = document.getElementById("avg_div")

    // Changes Button Text
    if (button.innerText === "Submit") {
        // TODO - Change this to whatever makes the screen next
        sendRating();
        button.innerText = "Next"
        avg_rating.style.display = "block"
    } else {
        // TODO - Change this to whatever makes the screen submit
        updateGenderChoice();
        loadImage();
        button.innerText = "Submit"
        avg_rating.style.display = "none"
    }


}

// Sends the value of the slider and image path to backend.py (game.html)
function sendRating() {
    var avg_rating = document.getElementById("avg_rating")
    var imagePath = document.getElementById("loadedImage").src;
    var sliderValue = document.getElementById("rating_slider").value;
    var genderChoice = localStorage.getItem("selectedOption");

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
        const rating = data.result
        avg_rating.innerText = rating
    });

}

// Keeps the dropdown consistent between pages
function saveSelectedOption() {
    var dropdown = document.getElementById("myDropdown");
    var selectedValue = dropdown.value;
    localStorage.setItem("selectedOption", selectedValue);
}

window.onload = function () {
    saveSelectedOption();
    updateGenderChoice();

    var currentPath = window.location.pathname;
    if (currentPath == "/leaderboard") {
        makeFilterDropdownChanges();
    }

    var dropdown = document.getElementById("myDropdown");
    var selectedValue = localStorage.getItem("selectedOption")

    if (!selectedValue) {
        selectedValue = "both";
        localStorage.setItem("selectedOption", selectedValue);
    }

    dropdown.value = selectedValue;
}

function updateGenderChoice() {
    var genderChoice = localStorage.getItem("selectedOption");

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
    if (currentPath == "/game") {
        var impath = document.getElementById("loadedImage").src
    
        // Check if an image change is needed
        if (dropdownValue == "both") {
            ;
        }
        else if (dropdownValue == "women") {
            if (!(impath.includes("/women"))) {
                loadImage();

                // TODO - CHANGE THIS TO WHATEVER YOU NEED TO MAKE THE NEXT SCREEN THE SUBMIT SCREEN
                var button = document.getElementById("gameButton");
                var avg_rating = document.getElementById("avg_div");
                button.innerText = "Submit"
                avg_rating.style.display = "none"
            }
        }
        else if (dropdownValue == "men") {
            if (!(impath.includes("/men"))) {
                loadImage();

                // TODO - CHANGE THIS TO WHATEVER YOU NEED TO MAKE THE NEXT SCREEN THE SUBMIT SCREEN
                var button = document.getElementById("gameButton");
                var avg_rating = document.getElementById("avg_div");
                button.innerText = "Submit"
                avg_rating.style.display = "none"
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
    var filterChoice = document.getElementById("filterDropdown").value;
    var genderChoice = localStorage.getItem("selectedOption");

    // Whenever you change the leaderboard to not bullets, you might have to change this
    var leaderboard = document.getElementById("leaderboard_list");
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
        // Makes the leaderboard with a for loop through all the ratings
        const ratings = data.result

        var leaderboard = document.getElementById("leaderboard_list")
        for (let i = 0, len = ratings.length; i < len; i++) {
            const listItem = document.createElement("li");
            listItem.textContent = ratings[i]
            leaderboard.appendChild(listItem)
        }
    });

    // On load in leaderboard.html, run this.
    // This will create the leaderboard elements & change them when dropdown changes
    // This way, I can use a python function to always make it correctly updated
}