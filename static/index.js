document.addEventListener("DOMContentLoaded", () => {
    const form          = document.getElementById("translateForm");
    const textInput     = document.getElementById("text");
    const sourceLang    = document.getElementById("sourceLang");
    const targetLang    = document.getElementById("targetLang");
    const translatedElt = document.getElementById("translatedText");
    const fileInput     = document.getElementById("fileInput");
  
    // — Text translation —
    form.addEventListener("submit", async e => {
      e.preventDefault();
      const text = textInput.value.trim();
      if (!text) return alert("Please enter text to translate.");
      translatedElt.innerHTML = "<em>Translating…</em>";
  
      try {
        const res = await fetch("/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            source: sourceLang.value,
            target: targetLang.value
          })
        });
        const data = await res.json();
        translatedElt.textContent = data.translatedText;
      } catch (err) {
        translatedElt.innerHTML = "<em>Error translating text.</em>";
        console.error(err);
      }
    });
  
    // — File upload + translate —
    fileInput.addEventListener("change", async e => {
      const file = e.target.files[0];
      if (!file) return;
  
      const fd = new FormData();
      fd.append("file", file);
      fd.append("source", sourceLang.value);
      fd.append("target", targetLang.value);
  
      try {
        const res  = await fetch("/upload", { method: "POST", body: fd });
        if (!res.ok) throw new Error();
        const blob = await res.blob();
        const a    = document.createElement("a");
        a.href     = URL.createObjectURL(blob);
        a.download = "translated_" + file.name;
        a.click();
      } catch (err) {
        translatedElt.innerHTML = "<em>Error translating text.</em>";
        console.error(err);
      }      
    });
  });
  