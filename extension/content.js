// Load the blacklist
    var blacklist = [];
    fetch('https://public-twitter-blacklist.s3.eu-central-1.amazonaws.com/blacklist.txt')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.text();
        })
        .then(data => {
            // The data is the content of the file
            blacklist = data.split('\n');
            console.log('Blacklist loaded:', blacklist);
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });

        function getUserHandle(tweetDiv) {
            // Get the element with data-testid="User-Name" within the specified tweetDiv
            var userNameElement = tweetDiv.querySelector('[data-testid="User-Name"]');
        
            if (userNameElement) {
                // Get all 'a' tags within the userNameElement
                var aTags = userNameElement.querySelectorAll('a');
                
                // Ensure there are at least two 'a' tags and get the text from the second one
                if (aTags.length >= 2) {
                    var textContent = aTags[1].textContent;
                    return textContent;
                }
            }
        
            return null;  // Return null if no matching user handle is found or there are not enough 'a' tags
        }
        
let printed_tweet_counter = 0
// Function to hide tweets from blacklisted users
function hideBlacklistedTweets() {
    // Get all tweet elements
    var tweets = document.querySelectorAll('[data-testid="tweet"]');
    for (var i = 0; i < tweets.length; i++) {
        var tweet = tweets[i];
                
        var userHandle = getUserHandle(tweet);
        console.log(userHandle);
        
        if (i<5 && printed_tweet_counter < 5) {
            printed_tweet_counter ++;
            // console.log(userHandle);
        }
        
        if (blacklist.includes(userHandle)) {
        // if (userHandle.match(/^@[A-Z]/)) {
        //     tweet.style.backgroundColor = 'yellow';
            tweet.style.display = 'none';
        }
    }
}

// Run the function every second to hide new tweets
setInterval(hideBlacklistedTweets, 1000);
