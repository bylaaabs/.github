# fonts

`Outfit.woff2` is [outfit](https://github.com/Outfitio/Outfit-Fonts), the one typeface of laaabs., under the SIL Open Font License 1.1 (`OFL.txt`), which allows embedding it. it is the variable font cut to weights 500 to 700 and to latin text, so every svg of the profile can carry it (12 KB) and render the same on any machine.

made from `Outfit[wght].ttf` of google/fonts with fonttools:

```sh
fonttools varLib.instancer 'Outfit[wght].ttf' wght=500:700 -o outfit-500-700.ttf
pyftsubset outfit-500-700.ttf --unicodes='U+0020-007E,U+00A0,U+00E1,U+00E9,U+00ED,U+00F3,U+00FA,U+00F1,U+2019,U+201C,U+201D,U+2026,U+20AC,U+2192' --layout-features=kern --flavor=woff2 --output-file=Outfit.woff2
```
