# 4cast Proposal

4cast is designed to provide easy-to-navigate weather forecasts to users of all demographics. In addition to allowing users to favorite locations for a personalized feed, there will be an option to opt into daily weather emails so that the user can wake up to an email outlining the weather for the day and  a blog of articles focused on the climate crisis to allow users to educate themselves on what is happening in the ecological world.

The application will provide location-specific current weather data, a 4-day forecast, and additional information for each location: high/low temperatures, option to have temperature in ˚C or ˚F, UV index, air quality, sunrise/sunset times, and more. The API’s I have found that I can potentially use are as follows:

    - https://www.weatherapi.com/ (weather)
    - https://openweathermap.org/api (weather)
    - https://docs.sendgrid.com/ (email)

The database schema will include a table for users (first_name, last_name, email, password, home_location, daily_email), and a table for fav_locations (user_id, location). For security purposes, I plan to use bcrypt hashing to store passwords. You can see the schema below.

![data model chart](images/datamodel)

In terms of functionality, I will allow users to sign up, log in, search for locations, favorite locations that they would like to see on their personalized home-page, edit their profile, and browse the climate blog. 
User flow is the path taken by a prototypical user on a website or app to complete a task. That being said, the user flow can be seen on the user flow chart below:

![user flow chart](images/userflow)

The application will start on the homepage. For non-registered users, the homepage will feature only the search bar. This allows them to search and get weather data for a specific location. Unregistered users are also allowed to look through the blog about climate and ecological issues our society is facing. From the homepage, users will have links to sign up or log in. Once logged in, the user’s home page will feature the search bar, their home location set at the time they registered, and any favorite locations. When a logged in user searches for a location, they are able to favorite that location so it shows up on their homepage. Logged in users are also able to visit their profile and update (or delete) it.