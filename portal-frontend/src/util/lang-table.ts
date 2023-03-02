export enum Language {
  None = "none",
  CSharp = "csharp",
  C = "c",
  Cpp = "cpp",
  Go = "go",
  Haskell = "haskell",
  Java = "java",
  Javascript = "javascript",
  Kotlin = "kotlin",
  Python = "python",
  Rust = "rust",
  Typescript = "typescript",
  Swift = "swift",
}

const langToExtsMap: Map<Language, string[]> = new Map([
  [Language.CSharp, [".cs"]],
  [Language.C, [".c"]],
  [Language.Cpp, [".cpp", ".cc", ".c++", ".C"]],
  [Language.Go, [".go"]],
  [Language.Haskell, [".hs"]],
  [Language.Java, [".java"]],
  [Language.Javascript, [".js"]],
  [Language.Kotlin, [".kt"]],
  [Language.Python, [".py"]],
  [Language.Rust, [".rs"]],
  [Language.Typescript, [".ts"]],
  [Language.Swift, [".swift"]],
]);

const langToCMSLangsMap: Map<Language, string[]> = new Map([
  [Language.CSharp, ["C# / Mono"]],
  [Language.C, ["C11 / gcc"]],
  [Language.Cpp, ["C++20 / g++", "C++17 / g++", "C++14 / g++", "C++1 / g++"]],
  [Language.Go, ["Go"]],
  [Language.Haskell, ["Haskell / ghc"]],
  [Language.Java, ["Java / JDK"]],
  [Language.Javascript, ["Javascript"]],
  [Language.Kotlin, ["Kotlin"]],
  [
    Language.Python,
    ["Python 3 / PyPy", "Python 3 / CPython", "Python 2 / CPython"],
  ],
  [Language.Rust, ["Rust"]],
  [Language.Typescript, ["Typescript"]],
  [Language.Swift, ["Swift"]],
]);

export function lookupCMSLang(cmsLang: string): Language {
  for (const [k, v] of langToCMSLangsMap)
    for (const x of v) if (x === cmsLang) return k;
  return Language.None;
}

export function langToCMSLang(lang: Language, cmsLangs: string[]): string {
  if (!cmsLangs.length) return "";
  const order = langToCMSLangsMap.get(lang);
  if (order === undefined) return cmsLangs[0];
  for (const ord of order) if (cmsLangs.includes(ord)) return ord;
  return "";
}

export function extToLang(extension: string): Language {
  for (const [k, v] of langToExtsMap)
    for (const x of v) if (x === extension) return k;
  return Language.None;
}
export function langToExt(lang: Language): string {
  const order = langToExtsMap.get(lang);
  return order === undefined ? "" : order[0];
}
