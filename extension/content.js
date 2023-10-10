

// Global Structure for User Lists
var curation_lists = {
    whitelists: {},
    blacklists: {}
};
var is_allowed_by_default = true;  // Set your default value

// Retrieve List Details from Chrome Storage
function getListDetailsFromStorage(callback) {
    chrome.storage.sync.get(null, function(items) {
        if (chrome.runtime.error) {
            console.error('Error fetching list details from storage:', chrome.runtime.error);
            return;
        }
        callback(items);
    });
}

// Fetch User Lists
function fetchUserLists(listDetails) {
    // Assuming listDetails is an array of objects each containing name, type, and id
    listDetails.forEach(detail => {
        const url = `'https://public-twitter-blacklist.s3.eu-central-1.amazonaws.com/blacklist.txt?name=${detail.name}&type=${detail.type}&id=${detail.id}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                curation_lists[detail.type][detail.name] = data.trim().split('\n');
            })
            .catch(error => console.error('Error fetching user list:', error));
    });
}

// Function to get user handle from tweet div
function getUserHandle(tweetDiv) {
    var userNameElement = tweetDiv.querySelector('[data-testid="User-Name"]');
    if (userNameElement) {
        var aTags = userNameElement.querySelectorAll('a');
        if (aTags.length >= 2) {
            var textContent = aTags[1].textContent;
            return textContent;
        }
    }
    return null;
}

// Tweet Filtering Function
function filterTweet(userHandle) {
    for (const listName in curation_lists.whitelists) {
        if (curation_lists.whitelists[listName].includes(userHandle)) {
            return true;  // Allow the tweet
        }
    }
    for (const listName in curation_lists.blacklists) {

        if (userHandle.match(/^@[A-Z]/)) {
        // if (curation_lists.blacklists[listName].includes(userHandle)) {

            return false;  // Disallow the tweet
        }
    }
    return is_allowed_by_default;  // If not found in either list, use the global default
}

// Function to hide blacklisted tweets
function clean_tweet_list() {
    var tweets = document.querySelectorAll('[data-testid="tweet"]');
    for (var i = 0; i < tweets.length; i++) {
        var tweet = tweets[i];
        var userHandle = getUserHandle(tweet);
        if (!filterTweet(userHandle)) {
            tweet.style.backgroundColor = 'yellow';
            // tweet.style.display = 'none';
        }
    }
}

// Regularly Update Tweet Display
setInterval(clean_tweet_list, 1000);

// Initiate the process
getListDetailsFromStorage(fetchUserLists);
