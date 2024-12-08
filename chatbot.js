
    document.getElementById("chatbot-form").addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent form from reloading the page

        const userInput = document.getElementById("chatbot-input").value;
        const messagesContainer = document.getElementById("chatbot-messages");

        if (userInput.trim() === "") return;

        // Display user's message in the chat
        const userMessage = document.createElement("div");
        userMessage.classList.add("chatbot-message");
        userMessage.innerHTML = `<p><strong>You:</strong> ${userInput}</p>`;
        messagesContainer.appendChild(userMessage);

        // Clear input field
        document.getElementById("chatbot-input").value = "";

        try {
            // Send the user's input to the backend
            const response = await fetch("/chatbot", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: userInput }),
            });

            const data = await response.json();

            // Display chatbot's reply
            const botMessage = document.createElement("div");
            botMessage.classList.add("chatbot-message");
            botMessage.innerHTML = `<p><strong>Bot:</strong> ${data.response || "Sorry, I couldn't understand that."}</p>`;
            messagesContainer.appendChild(botMessage);

            // Scroll to the latest message
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } catch (error) {
            console.error("Error:", error);
            const errorMessage = document.createElement("div");
            errorMessage.classList.add("chatbot-message");
            errorMessage.innerHTML = `<p><strong>Bot:</strong> An error occurred. Please try again later.</p>`;
            messagesContainer.appendChild(errorMessage);
        }
    });

