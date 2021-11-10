const BASE_URL = "http://localhost:5000" 

async function removeFav(target, id){
    await axios.post(`${BASE_URL}/unfavorite/${id}`)
}

async function addFav(location){
    await axios.post(`${BASE_URL}/favorite/${location}`);
}

// Remove favorite location from homepage
$("#weather-card").on("click", ".remove-fav", async function (evt){
    evt.preventDefault();
    const weatherCard = $(evt.target).parent().parent().parent().parent();
    const weatherCardID = weatherCard.attr("data-location-id")
    removeFav(weatherCard, weatherCardID)
    target.remove()
})

// Remove favorite location from search page
$("#search-weather-card").on("click", ".remove-fav", async function (evt){
    evt.preventDefault();
    const weatherCard = $(evt.target).parent().parent().parent().parent();
    const weatherCardID = weatherCard.attr("data-location-id")
    removeFav(weatherCard, weatherCardID)
    window.location.reload()
})

// Add favorite location from search page
$("#search-weather-card").on("click", ".add-fav", async function (evt){
    evt.preventDefault();
    const weatherCard = $(evt.target).parent().parent().parent().parent();
    const location = weatherCard.attr("data-location-name")
    addFav(location)
    window.location.reload()
})