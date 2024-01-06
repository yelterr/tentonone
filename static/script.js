
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
            const url = data.result;

            // Set the image source dynamically
            document.getElementById('loadedImage').src = url;
        });
}

// Handles the "next" page when a user submits.
function showAndRemoveNext() {
    var button = document.getElementById("gameButton")
    var avg_rating = document.getElementById("avg_div")

    // Changes Button Text
    if (button.innerText === "Submit") {
        sendRating();
        button.innerText = "Next"
        avg_rating.style.display = "block"
    } else {
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

// Gets the value of the rating slider (game.html)
var slider = document.getElementById("rating_slider");
var output = document.getElementById("slider_value");
output.innerHTML = slider.value;

slider.oninput = function() {
  output.innerHTML = this.value;
}