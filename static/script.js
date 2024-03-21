// Changes the image (game.html)
function loadImage() {
    var genderChoice = sessionStorage.getItem("selectedOption");
    var sessionID = sessionStorage.getItem("sessionID");

    fetch('/get_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'gender_choice': genderChoice, "sessionID": sessionID }),
    })
    .then(response => response.json())
    .then(data => {
            const url = data.result.impath;
            const name = data.result.name;
            var source = data.result.source;
            var source_type = data.result.source_type;

            source = makeSourceGreatAgain(source, source_type);

            // Set the image source dynamically
            document.getElementById('loadedImage').src = url;
            document.getElementById('name-overlay').innerText = name;
            document.getElementById("name-bottom").innerText = name;
            document.getElementById("name_result").innerText = name;
            document.getElementById("source-element").innerHTML = source;
        });
}

// Handles the "next" page when a user submits.
function showAndRemoveNext() {
    var button = document.getElementById("gameButton");

    // Making sessionID if it doesn't exist yet.
    if (sessionStorage.getItem("sessionID") != null && sessionStorage.getItem("sessionID") != "") {
        ;
    }
    else {
        sessionStorage.setItem('sessionID', generateRandomString(30));
    }

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
    
    loadImage();
    button.innerHTML = "Submit <span id='final-number'></span>/10"
    var default_value = getRandomNumberWithDecimal(minValue, maxValue);
    slider.value = default_value
    textInput.value = default_value

    revealed.style.display = "none"
    submit_to_reveal.style.display = "block"
    
    leaderboard_button.style.display = "none"

    slider.disabled = false;
    textInput.disabled = false;
    document.getElementById("final-number").innerText = default_value;
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
    var sessionID = sessionStorage.getItem("sessionID")
    var grammer_place = document.getElementById("useless-functionality");

    var avg_rating_txt = document.getElementById("avg_rating")
    var amt_raters_txt = document.getElementById("amt_raters")
    var ranking_txt = document.getElementById("ranking")

    // Make an AJAX request to send the slider value to the server
    fetch('/send_rating', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'slider_value': sliderValue, "image_path": imagePath , "sessionID": sessionID}),
    })
    .then(response => response.json())
    .then(data => {
        // Changes the avg_rating text to the actual average rating
        const rating = data.result.rating
        const amt_raters = data.result.amt_raters
        const ranking = data.result.ranking

        avg_rating_txt.innerText = rating
        amt_raters_txt.innerText = amt_raters
        var persons = "people";
        if (amt_raters == 1) {
            var persons = "person"
        }
        grammer_place.innerText = persons;
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

    sessionStorage.setItem("selectedOption", selectedValue);
}

window.onload = function () {
    // Making sessionID if it doesn't exist yet.
    if (sessionStorage.getItem("sessionID") != null && sessionStorage.getItem("sessionID") != "") {
        ;
    }
    else {
        sessionStorage.setItem('sessionID', generateRandomString(30));
    }

    var currentPath = window.location.pathname;
    if (currentPath == "/leaderboard") {
        loadLeaderboard();
    }

    var dropdown = document.getElementById("myDropdown");
    var selectedValue = sessionStorage.getItem("selectedOption")
    const choices = ["both", "men", "women"]

    if (!selectedValue || !choices.includes(selectedValue)) {
        selectedValue = "both";
        sessionStorage.setItem("selectedOption", selectedValue);
    }

    dropdown.value = selectedValue;
}

// Whenever the gender dropdown changes, make changes depending on the page
function makeGenderDropdownChanges() {
    saveSelectedOption();
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
                makeSubmit();
            }
        }
        else if (dropdownValue == "men") {
            if (!(impath.includes("/men"))) {
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
        // Filter the leaderboard for men or women
        var leaderboard = document.getElementById("leaderboard-background")
        editLeaderboardGender(leaderboard);
        searchLeaderboard(leaderboard);
    }
}

var current_filter = "h2l"
function makeFilterDropdownChanges() {
    var filterChoice = document.getElementById("filterDropdown").value;

    if (filterChoice != current_filter) {
        var leaderboard = document.getElementById("leaderboard-background")
        var children = leaderboard.children;
        var childrenArray = Array.from(children);
        childrenArray = childrenArray.reverse()
        childrenArray.forEach(function(child) {
            leaderboard.removeChild(child);
        });

        for (let i = 0, len = childrenArray.length; i < len; i++) {
            leaderboard.appendChild(childrenArray[i])
        }

        current_filter = filterChoice;
    }
}

function loadLeaderboard() {
    var genderChoice = sessionStorage.getItem("selectedOption");
    var filterChoice = document.getElementById("filterDropdown").value;
    current_filter = filterChoice;

    var leaderboard = document.getElementById("leaderboard-background")
    var children = leaderboard.children;
    var childrenArray = Array.from(children);

    // Just in case. The leaderboard should be empty anyways, but you never know
    childrenArray.forEach(function(child) {
        leaderboard.removeChild(child);
    });

    fetch('/retrieve_ratings')
        .then(response => response.json())
        .then(data => {
            // I need POSITION, NAME, RATING, AMT_RATERS, IMPATH
            const rankings = data.result

            // (margaret_thatcher.jpg, 38, 7.99211, 1, Joao Pereira, https://yourmom.com, link)
            for (let i = 0, len = rankings.length; i < len; i++) {
                var impath = rankings[i][0];
                var amt_raters = rankings[i][1]
                var rating = rankings[i][2]
                var name = rankings[i][3]
                var source = rankings[i][4]
                
                /* JUST IN CASE I NEED TO HAVE SOURCES ON THE LEADERBOARD IN THE FUTURE */
                /*
                var source_type = rankings[i][5]
                source = makeSourceGreatAgain(source, source_type)
                */
                

                // Getting data-category correct
                var gender = NaN;
                if (impath.includes("/men")) {
                    gender = "men";
                }
                else if (impath.includes("/women")) {
                    gender = "women"
                }

                var persons = "people";
                // People vs. Person
                if (amt_raters == 1) {
                    var persons = "person";
                }

                var gorlock = "";
                if (name == "Ali C. Lopez") {
                    gorlock = "Gorlock the Destroyer"
                }

                const leaderboard_item = document.createElement("div");
                leaderboard_item.dataset.category = gender
                leaderboard_item.className = "leaderboard-element"
                leaderboard_item.innerHTML = `                    
                    <div class="position-div">
                        <p class="position-txt" id="position-txt">${i+1}</p>
                    </div>

                    <!--
                    <div style="position: relative; height: 100%;">
                        ${source}
                    </div>
                    -->

                    <div class="not-position-div">
                        <img class="leaderboard-img" src="${impath}" loading="lazy">

                        <div class="name-and-raters">
                            <p class="name-txt" style="margin: 0; padding: 0;">${name}</p>
                            <p class="rated-by">rated by ${amt_raters} ${persons}</p>
                        </div>

                        <div class="rating-div">
                            <div class="has-the-numbers">
                                <p class="number-txt" style="margin: 0; padding: 0;">${rating}</p>
                                <p class="out-of-ten" style="margin-top: 3px; padding: 0;">/10</p>
                            </div>
                        </div>
                    </div>

                    <span style="display: none;">${gorlock}</span>
                    `

                // Make initial filter dropdown changes
                if (filterChoice == "l2h") {
                    leaderboard.insertBefore(leaderboard_item, leaderboard.firstChild);
                }
                else {
                    leaderboard.appendChild(leaderboard_item)
                }
            }

            // Make leaderboard gender changes
            leaderboard = editLeaderboardGender(leaderboard)
            //console.log(leaderboard.children[0])

            // Filtering the new leaderboard elements for anything already in the search bar
            leaderboard = searchLeaderboard(leaderboard)

    });
}

function editLeaderboardGender(leaderboard_element) {
    var genderChoice = sessionStorage.getItem("selectedOption");

    var children = leaderboard_element.children;
    var childrenArray = Array.from(children);

    for (let i = 0, len = childrenArray.length; i < len; i++) {
        var category = children[i].getAttribute("data-category");
        if (genderChoice == "both") {
            children[i].style.display = "flex";
        }
        else {
            if (category == genderChoice) {
                children[i].style.display = "flex"
            }
            else {
                children[i].style.display = "none";
            }
        }
    }

    leaderboard_element = changePositionText(leaderboard_element)

    return leaderboard_element;
}

function searchLeaderboard(leaderboard_element, searchInput) {
    var searchInput = document.getElementById("searchInput");
    const searchTerm = searchInput.value.toLowerCase();

    const elements = leaderboard_element.children;
    var genderChoice = sessionStorage.getItem("selectedOption");

    for (let i = 0; i < elements.length; i++) {
        const elementText = elements[i].textContent.toLowerCase();
        var category = elements[i].getAttribute("data-category");

        if (genderChoice == "both" || category == genderChoice) {
            if (elementText.includes(searchTerm)) {
                elements[i].style.display = "flex";
            }
            else {
                elements[i].style.display = "none";
            }
        }
        else {
            elements[i].style.display = "none";
        }
    }


    return leaderboard_element;
}

// Changes position number for men, women, both
function changePositionText(leaderboard_element) {
    var childrenArray = Array.from(leaderboard_element.children);
    var genderChoice = sessionStorage.getItem("selectedOption");
    var filterChoice = document.getElementById("filterDropdown").value;

    if (filterChoice == "l2h") {
        childrenArray = childrenArray.reverse()
    }

    var current_position = 1;
    for (let i = 0; i < childrenArray.length; i++) {
        var category = childrenArray[i].getAttribute("data-category");
        if (genderChoice == "both" || category == genderChoice) {
            var position_text = childrenArray[i].querySelector('#position-txt');
            position_text.innerText = current_position;
            current_position += 1;
        }
    }

    if (filterChoice == "l2h") {
        childrenArray = childrenArray.reverse()
    }

    leaderboard_element.innerHTML = '';
    childrenArray.forEach(function(child) {
        leaderboard_element.appendChild(child);
    });

    return leaderboard_element;
}

function makeSourceGreatAgain(source, source_type) {
    if (source_type == "wiki") {
        // Decode the <> signs
        var dummyElement = document.createElement('div');
        dummyElement.innerHTML = source;
        var decodedString = dummyElement.innerText;

        source = `<p class="overlay-source">${source}</p>`
        if (decodedString.length > 64) {
            var links = dummyElement.children
            var link_one = links[0].href
            var link_two = links[1].href

            var source_name = decodedString.slice(0,20); // Link 1
            var cc_by_sa = decodedString.slice(-34,-22); // Link 2
            var via_commons = decodedString.slice(-21,); // Just text
            
            source = `<p class="overlay-source"><a href=${link_one}>${source_name}</a> <a href=${link_two}>${cc_by_sa}</a> ${via_commons}</p>`
            return source
        }

        dummyElement.remove()
        return source
    }
    else if (source_type == "link") {
        source = `<p class="overlay-source">Source: <a href="${source}">Link</a></p>`
        return source
    }
    else {
        source = `<p class="overlay-source">Credit: ${source}</p>`
        return source
    }
}

function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    let result = '';
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * characters.length);
      result += characters.charAt(randomIndex);
    }

    return result;
}

// Function to generate a random number with one decimal point
function getRandomNumberWithDecimal(min, max) {
    // Generate a random integer within the range
    const randomInteger = Math.floor(Math.random() * (max - min + 1)) + min;

    // Generate a random decimal digit (0-9)
    const randomDecimal = Math.floor(Math.random() * 10);

    // Combine the integer and decimal parts to form the final number
    const randomNumberWithDecimal = randomInteger + (randomDecimal / 10);

    return randomNumberWithDecimal;
}