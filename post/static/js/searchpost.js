const searchInput = document.getElementById("searchInput");
const resultsDiv = document.getElementById("searchResults");
let debounceTimer;

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function debounce(func, delay) {
    return function (...args) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(this, args), delay);
    };
}

async function fetchSearchResults(query) {
    if (!query.trim()) {
        resultsDiv.style.display = "none";
        resultsDiv.innerHTML = "";
        return;
    }

    try {
        const response = await fetch(`/search/post?query=${encodeURIComponent(query)}`, {
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
        });

        const data = await response.json();

        if (data.results && data.results.length > 0) {
            resultsDiv.innerHTML = data.results
                .map(
                    (post) =>
                        `<div class="post-card" onclick="scrollToPostAndCloseSearch('${post.id}')" style="cursor: pointer;">
                                    
                                    <div class="post-content">
                                        <div class="post-meta">
                                            <div class="post-category" style="background-color: var(--primary); color: white;">${post.tags[0]}</div>

                                        </div>
                                        <h3 class="post-title">${post.title}</h3>
                                        <p class="post-excerpt">${post.content}</p>
                                        <div class="post-footer">
                                            <div class="post-author">
                                                <span>By <b>${post.posted_by}</b></span>
                                            </div>
                            
                                        </div>
                                    </div>
                                </div>
                            `
                )
                .join("");
            resultsDiv.style.display = "block";
        } else {
            resultsDiv.innerHTML = `<p style="color: var(--text-dim); text-align: center;">No results found</p>`;
            resultsDiv.style.display = "block";
        }
    } catch (err) {
        console.error("Search request failed:", err);
        resultsDiv.style.display = "none";
    }
}
function scrollToPostAndCloseSearch(postId) {
    console.log("Function called!");

    const element = document.getElementById(`post-${postId}`);
    if (element) {
        element.scrollIntoView({ behavior: "smooth" });
        element.style.transition = "background-color 0.4s ease";
        element.style.backgroundColor = "rgba(99, 102, 241, 0.1)"; // light accent

        setTimeout(() => {
            element.style.backgroundColor = "";
        }, 1200);
        // Hide and clear the search results
        const resultsDiv = document.getElementById("searchResults"); // replace with your actual ID
        if (resultsDiv) {
            resultsDiv.style.display = "none";
            resultsDiv.innerHTML = "";
        }

        // Also clear the input if needed
        // const searchInput = document.getElementById("searchInput"); // replace with your actual input ID
        // if (searchInput) {
        //     searchInput.value = "";
        // }
    }
}
searchInput.addEventListener(
    "input",
    debounce(() => {
        const query = searchInput.value;
        fetchSearchResults(query);
    }, 500)
);
