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
}

const cmsLangLookup: Record<string, Language> = {
  "C++11 / g++": Language.Cpp,
  "C++14 / g++": Language.Cpp,
  "C++17 / g++": Language.Cpp,
  "C++20 / g++": Language.Cpp,
  "C11 / gcc": Language.C,
  "C# / Mono": Language.CSharp,
  "Haskell / ghc": Language.Haskell,
  "Java / JDK": Language.Java,
  "Python 2 / CPython": Language.Python,
  "Python 3 / CPython": Language.Python,
  "Python 3 / PyPy": Language.Python,
  Rust: Language.Rust,
  Go: Language.Go,
  Javascript: Language.Javascript,
  Kotlin: Language.Kotlin,
  Typescript: Language.Typescript,
};
const extensionLangLookup: Record<string, Language> = {
  ".c": Language.C,
  ".cpp": Language.Cpp,
  ".cc": Language.Cpp,
  ".cxx": Language.Cpp,
  ".c++": Language.Cpp,
  ".C": Language.Cpp,
  ".cs": Language.CSharp,
  ".hs": Language.Haskell,
  ".java": Language.Java,
  ".py": Language.Python,
  ".rs": Language.Rust,
  ".kt": Language.Kotlin,
  ".go": Language.Go,
  ".js": Language.Javascript,
  ".ts": Language.Typescript,
};
const langExtenionsLookup: Map<Language, string> = new Map([
  [Language.None, ""],
  [Language.CSharp, ".cs"],
  [Language.C, ".c"],
  [Language.Cpp, ".cpp"],
  [Language.Go, ".go"],
  [Language.Haskell, ".hs"],
  [Language.Java, ".java"],
  [Language.Javascript, ".js"],
  [Language.Kotlin, ".kt"],
  [Language.Python, ".py"],
  [Language.Rust, ".rs"],
  [Language.Typescript, ".ts"],
]);

export function lookupCMSLang(cmsLang: string): Language {
  return cmsLang in cmsLangLookup ? cmsLangLookup[cmsLang] : Language.None;
}

export function langToCMSLang(lang: Language, cmsLangs: string[]): string {
  if (lang === Language.Cpp) {
    for (const ord of [
      "C++20 / g++",
      "C++17 / g++",
      "C++14 / g++",
      "C++11 / g++",
    ]) {
      if (cmsLangs.includes(ord)) return ord;
    }
  }
  if (lang === Language.Python) {
    for (const ord of [
      "Python 3 / CPython",
      "Python 3 / PyPy",
      "Python 2 / CPython",
    ])
      if (cmsLangs.includes(ord)) return ord;
  }
  for (const cmsLang in cmsLangLookup) {
    if (cmsLangs.includes(cmsLang)) {
      return cmsLangLookup[cmsLang];
    }
  }
  return cmsLangs.length ? cmsLangs[0] : "";
}

export function extToLang(extension: string): Language {
  return extension in extensionLangLookup
    ? extensionLangLookup[extension]
    : Language.None;
}
export function langToExt(lang: Language): string {
  return langExtenionsLookup.get(lang) || "";
}
