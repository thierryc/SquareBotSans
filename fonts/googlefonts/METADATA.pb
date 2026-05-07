name: "Square Bot Sans"
designer: "Thierry Charbonnel"
license: "OFL"
category: "SANS_SERIF"
date_added: "2026-05-07"
fonts {
  name: "Square Bot Sans"
  style: "normal"
  weight: 400
  filename: "SquareBotSans[wdth,wght].ttf"
  post_script_name: "SquareBotSans-Regular"
  full_name: "Square Bot Sans Regular"
  copyright: "Copyright 2024 The SquareBot Sans Project Authors (https://github.com/thierryc/SquareBotSans)"
}
fonts {
  name: "Square Bot Sans"
  style: "italic"
  weight: 400
  filename: "SquareBotSans-Italic[wdth,wght].ttf"
  post_script_name: "SquareBotSans-Italic"
  full_name: "Square Bot Sans Italic"
  copyright: "Copyright 2024 The SquareBot Sans Project Authors (https://github.com/thierryc/SquareBotSans)"
}
subsets: "latin"
subsets: "latin-ext"
subsets: "menu"
subsets: "vietnamese"
axes {
  tag: "wdth"
  min_value: 75.0
  max_value: 125.0
}
axes {
  tag: "wght"
  min_value: 200.0
  max_value: 900.0
}
source {
  repository_url: "https://github.com/thierryc/SquareBotSans"
  branch: "main"
  config_yaml: "sources/config.yaml"
  files {
    source_file: "fonts/googlefonts/SquareBotSans[wdth,wght].ttf"
    dest_file: "SquareBotSans[wdth,wght].ttf"
  }
  files {
    source_file: "fonts/googlefonts/SquareBotSans-Italic[wdth,wght].ttf"
    dest_file: "SquareBotSans-Italic[wdth,wght].ttf"
  }
  files {
    source_file: "OFL.txt"
    dest_file: "OFL.txt"
  }
  files {
    source_file: "documentation/DESCRIPTION.en_us.html"
    dest_file: "DESCRIPTION.en_us.html"
  }
}
