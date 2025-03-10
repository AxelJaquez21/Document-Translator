document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("translateForm");
    const textInput = document.getElementById("text");
    const sourceLang = document.getElementById("sourceLang");
    const targetLang = document.getElementById("targetLang");
    const translatedText = document.getElementById("translatedText");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const text = textInput.value.trim();
        if (!text) {
            alert("Please enter text to translate.");
            return;
        }
        
        translatedText.innerHTML = "<em>Translating...</em>";
        translatedText.style.color = "#555";
        
        try {
            const response = await fetch("/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text,
                    source: sourceLang.value,
                    target: targetLang.value
                })
            });
            
            const data = await response.json();
            translatedText.textContent = data.translated_text || "Translation failed.";
            translatedText.style.color = "#000";
            translatedText.style.fontWeight = "bold";
            translatedText.style.transition = "opacity 0.5s ease-in-out";
            translatedText.style.opacity = 1;
        } catch (error) {
            console.error("Error during translation:", error);
            translatedText.textContent = "Error translating text.";
            translatedText.style.color = "red";
        }
    });
});
