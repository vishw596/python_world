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
        const response = await fetch(`/search/article?query=${encodeURIComponent(query)}`, {
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
        });

        const data = await response.json();

        if (data.results && data.results.length > 0) {
            resultsDiv.innerHTML = data.results
                .map(
                    (article) => `
                                <div class="article-card" onclick="window.location.href='/article/${article.id}'" style="cursor: pointer;">
                                    
                                    <div class="article-content">
                                        <div class="article-meta">
                                            <div class="article-category" style="background-color: var(--primary); color: white;">${article.topic}</div>

                                        </div>
                                        <h3 class="article-title">${article.title}</h3>
                                        <p class="article-excerpt">${article.description}</p>
                                        <div class="article-footer">
                                            <div class="article-author">
                                                <span>By <b>${article.source}</b></span>
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

searchInput.addEventListener(
    "input",
    debounce(() => {
        const query = searchInput.value;
        fetchSearchResults(query);
    }, 1000)
);
