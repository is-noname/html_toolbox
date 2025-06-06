Kurz und knapp:

1. **Im `<head>` den `<style>`-Block öffnen**
   Dort stehen alle Farbwerte.

2. **Haupttext & Hintergrund**

   ```css
   body {
     background: #fff;    /* Seiten-Hintergrund */
     color: #333;         /* Textfarbe */
   }
   ```

3. **Code-Inline**

   ```css
   code {
     background: #f5f5f5; /* Hintergrund für `code` */
   }
   ```

4. **Code-Blöcke**

   ```css
   pre {
     background: #2d2d2d; /* Block-Hintergrund */
     color:     #ccc;     /* Block-Textfarbe */
   }
   ```

5. **Drop-Area Rahmen/Schrift**

   ```css
   #drop {
     border:      2px dashed #ccc; /* Rahmen */
     color:       #666;            /* Hinweis-Text */
   }
   /* z.B. bei Hover */
   #drop.dragover {
     border-color: #444;
   }
   ```

6. **Highlight.js-Theme wechseln**
   Die Zeile

   ```html
   <link rel="stylesheet" href="…/github-dark.min.css">
   ```

   gegen ein anderes Theme austauschen (z. B. `atom-one-light.css`).

Speichern, Seite neu laden – fertig!
