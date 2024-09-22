// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    var query = '';
    localStorage.setItem('apiBaseUrl', baseUrl);

    if (document.getElementById('sort').checked) {
        var sortKey = document.querySelector('.sort-param input[type=radio]:checked').id.slice(0,-5)
        if (document.querySelector('.sort-param input[type=checkbox]:checked')) {var direction = 'desc'}
        else {var direction = 'asc'};
        query = '?sort=' + sortKey + '&direction=' + direction
    }
    console.log(query)
    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts' + query)
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = document.createElement('div');
                if (post.likes == undefined) {post.likes = 0};
                postDiv.className = 'post';
                postDiv.innerHTML = `
                <div class="post-info">
                    <h2 title="Post id ${post.id}">${post.title}</h2>
                    <p class="post-meta"><em>Author: ${post.author}</em><br>
                    <em>Publish date: ${post.date}</em></p>
                    <p>${post.content}</p>
                </div>
                <div class="post-buttons">
                    <button onclick="deletePost(${post.id})">Delete</button>
                    <p class="likes">${post.likes} <span class="emoji" onclick="likePost(${post.id})">👍</span></p>
                </div>
                `;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent, author: postAuthor })
    })
    .then(response => response.json())  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}


// Function to send a GET request to the specific post's like endpoint
function likePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value
    fetch(baseUrl + '/posts/' + postId + '/like', {method: 'GET'})
    .then(response => {
        console.log('Post got one like:', postId);
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}

function loadParamToggle(elemId) {
    if (document.getElementById(elemId).checked) {
        document.getElementsByClassName('search-params')[0].style.display = 'none';
        document.getElementsByClassName('sort-params')[0].style.display = 'none';
        document.getElementsByClassName(elemId + '-params')[0].style.display = 'grid';
    }
}
