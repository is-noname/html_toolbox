Das Design und Styling des Code Formatters (`code_saver.html`) kannst du direkt im `<style>`-Block im `<head>`-Bereich ändern. Hier ein Überblick über relevante Abschnitte und was sie beeinflussen:

---

### 🎨 **Hintergrund und Textfarben**

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f5f5;  /* Heller Hintergrund */
  color: #333;          /* Dunkle Schriftfarbe */
}
```

→ Passe `background` und `color` an für Dark Mode oder andere Farbschemata.

---

### 🧾 **Codefeld (Textarea)**

```css
#code {
  width: 100%;
  height: 400px;
  font-family: monospace;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
```

→ Hier kannst du Schriftgröße, Rand, Hintergrund oder Scrollverhalten ändern.

---

### 🔘 **Format-Buttons**

```css
.format-option {
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}
.format-option.active {
  background: #ddd;
}
```

→ Willst du visuelles Feedback beim Auswählen ändern, passe `.active` an.

---

### 🪧 **Status-Anzeige (oben rechts eingeblendet)**

```css
#status {
  position: fixed;
  top: 10px;
  right: 10px;
  padding: 10px;
  border-radius: 4px;
  display: none;
}
```

→ Die Hintergrundfarbe für Erfolg/Misserfolg wird dynamisch im Skript gesetzt (siehe `showStatus()`).

---

Wenn du global das Design updaten willst (z. B. auf dunkel), ändere:

* `body { background: #121212; color: #f0f0f0; }`
* alle hellen Hintergrundwerte wie `#f5f5f5`, `#ddd`, `#ccc` entsprechend ersetzen (z. B. durch `#333`, `#555`).

Sag Bescheid, wenn du ein konkretes Theme (z. B. Dark Mint Modern) willst – dann mache ich dir das als Style-Update.
