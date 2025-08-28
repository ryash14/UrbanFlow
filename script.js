const API_KEY = 'AIzaSyCHRdbPzRTqaE2Q76-vpyEv7bSdWvjB_sM';
const API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent';

document.getElementById("chat-button").addEventListener("click", function () {
    document.getElementById("chat-container").classList.remove("hidden");
    document.getElementById("chat-button").classList.add("hidden");
});

document.getElementById("close-chat").addEventListener("click", function () {
    document.getElementById("chat-container").classList.add("hidden");
    document.getElementById("chat-button").classList.remove("hidden");
});

document.getElementById("chat-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        document.getElementById("send-chat").click();
    }
});

document.getElementById("send-chat").addEventListener("click", async function () {
    let inputField = document.getElementById("chat-input");
    let message = inputField.value.trim();
    let chatBox = document.getElementById("chat-box");

    if (message !== "") {
        // Append User Message
        let userMessage = document.createElement("div");
        userMessage.className = "bg-blue-500 p-3 rounded-lg shadow-md text-sm self-end text-white";
        userMessage.textContent = message;
        chatBox.appendChild(userMessage);
        chatBox.scrollTop = chatBox.scrollHeight;

        inputField.value = "";
        
        try {
            // Fetch AI-generated response as a Traffic Assistant
            let botResponse = await getTrafficResponse(message);

            // Append Bot Response
            let botMessage = document.createElement("div");
            botMessage.className = "bg-gray-700 p-3 rounded-lg shadow-md text-sm self-start text-white";
            botMessage.textContent = botResponse;
            chatBox.appendChild(botMessage);
            chatBox.scrollTop = chatBox.scrollHeight;
        } catch (error) {
            console.error("Error:", error);
            
            let errorMessage = document.createElement("div");
            errorMessage.className = "bg-red-500 p-3 rounded-lg shadow-md text-sm self-start text-white";
            errorMessage.textContent = "⚠️ Unable to fetch traffic data. Please try again.";
            chatBox.appendChild(errorMessage);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }
});

// Function to fetch AI-generated traffic response
async function getTrafficResponse(userQuery) {
    const response = await fetch(`${API_URL}?key=${API_KEY}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [
                {
                    parts: [
                        { text: `You are a chatbot. Give answers fot this question: ${userQuery}. Do NOT ask follow-up questions. Directly provide information.` }
                    ]
                }
            ]
        })
    });

    if (!response.ok) throw new Error("Failed to generate response");

    const data = await response.json();
    return data.candidates[0].content.parts[0].text || "🚦 Unable to get real-time traffic updates at the moment.";
}
