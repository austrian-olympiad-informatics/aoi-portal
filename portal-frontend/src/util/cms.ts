export function translateText(text: string[]) {
  if (!text.length) return "";
  const s = text[0];
  if (s === "Execution timed out") return "Zeitüberschreitung bei Ausführung";
  if (s === "Execution timed out (wall clock limit exceeded)")
    return "Zeitüberschreitung bei Ausführung (Echtzeit-Limit überschritten)";
  if (s === "Output is correct") return "Ausgabe korrekt";
  if (s === "Output is partially correct") return "Ausgabe teilweise korrekt";
  if (s === "Output isn't correct") return "Ausgabe nicht korrekt";
  if (s === "Execution killed (could be triggered by violating memory limits)")
    return "Ausführung terminiert (könnte durch Überschreiten der Speicherbegrenzung ausgelöst worden sein)";
  if (s === "Execution failed because the return code was nonzero")
    return "Ausführung wegen Rückgabewert ungleich 0 fehlgeschlagen";
  return s;
}
