# Recall / Feynman bei nicht angemeldeten Nutzern

UX-Handling: Nutzer, die nicht angemeldet sind, können keine KI-Auswertung durchführen.

- Aktivität wird normal angezeigt, bei Recall so weit, bis die Textfelder für die Antworten und der Button "Antworten prüfen" erscheinen.
- Das Textfeld wird nicht angezeigt bzw. durch einen Login-Hinweis ersetzt.
    - Keine Eingabe möglich.
    - Der Nutzer erfährt unmittelbar, dass für die KI-Auswertung eine Anmeldung erforderlich ist.
- Der Hinweis enthält einen klaren „Anmelden“-/„Registrieren“-Button.
- Der Nutzer wird nach der Anmeldung direkt zur gleichen Recall-/Feynman-Aufgabe zurückgeführt.
- Dort ist das normale Textfeld aktiv, sodass er seine Antwort eingeben kann.
- Der „Antworten überprüfen / Jetzt Auswerten“-Button ist für nicht angemeldete Nutzer deaktiviert.


Damit gilt als Grundprinzip:

Nicht angemeldet → keine Eingabe → Login → zurück zur Aufgabe → Eingabe → Auswertung.

Wichtig ist dabei: Der Nutzer wird nicht erst nach dem Schreiben seiner Antwort mit der Login-Anforderung konfrontiert. Dadurch entsteht keine Situation, in der er eine Antwort verfasst, von der er anschließend erwartet, dass sie ausgewertet wird, obwohl das technisch noch gar nicht möglich ist.

Zusatz: Es gibt ja Limits dazu, wie viele Auswertungen ein User machen kann. Falls der User angemeldet ist und der user am Limit ist (also so, dass deswegen keine KI-Auswertung mehr möglich ist), dann wird ähnlich wie oben statt dem Textfeld ein Hinweis angezeigt, dass er das Limit erreicht hat. Der Button „Antworten prüfen / Jetzt Auswerten“ ist dann deaktiviert.

# Weiteres

Im Übrigen sollte man hier „Antworten prüfen / Jetzt Auswerten“ für recall und feynman einen einheitlichen Text nehmen.

Aktuell kommt während der KI-Ausertung (bei recall und feynman) auf dem button der text "MatheChecks prüft ...". Das könnte theoretisch bleiben, aber ich möchte allgemein einen deutlicheren (vielleicht sogar "coolen") Effekt dafür haben, dass die KI gerade arbeitet. Häufig sieht man ja in solchen Situtionen z.B. so ein generisches Overlay mit leichtem Farbspiel oder zumindest Animationen am Rand. Dieser Effekt könnte sich entweder auf den Button beschränken, oder - falls das zu wenig ist - sogar die ganze Recall/Feynman-Karte betreffen.