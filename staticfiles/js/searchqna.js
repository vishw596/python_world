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
        const response = await fetch(`/search/qna?query=${encodeURIComponent(query)}`, {
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
        });

        const data = await response.json();

        if (data.results && data.results.length > 0) {
            resultsDiv.innerHTML = data.results
                .map(
                    (qna) =>
                        `<div class="qna-card" onclick="scrollToqnaAndCloseSearch('${qna.id}')" style="cursor: pointer;">
                                    <div class="qna-content">
                                        <h3 class="qna-title">${qna.title}</h3>
                                        <p class="qna-excerpt">${qna.content}</p>
                                        <div class="qna-footer">
                                            <div class="qna-author">
                                                <span>By <b>${qna.posted_by}</b></span>
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
function scrollToqnaAndCloseSearch(qnaId) {
    console.log("Function called!");

    const element = document.getElementById(`question-${qnaId}`);
    if (element) {
        element.scrollIntoView({ behavior: "smooth" });

        // Highlight effect
        element.style.transition = "background-color 0.4s ease";
        element.style.backgroundColor = "rgba(99, 102, 241, 0.1)"; // light accent

        setTimeout(() => {
            element.style.backgroundColor = "";
        }, 1200);

        // Hide and clear search
        const resultsDiv = document.getElementById("searchResults");
        if (resultsDiv) {
            resultsDiv.style.display = "none";
            resultsDiv.innerHTML = "";
        }
    }
}

searchInput.addEventListener(
    "input",
    debounce(() => {
        const query = searchInput.value;
        fetchSearchResults(query);
    }, 500)
);

// <div class="qna-meta">
{/* <div class="qna-category" style="background-color: var(--primary); color: white;">${qna.tags[0]}</div>
</div> */}