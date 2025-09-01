# Сервис знакомств по обищм лайкам. 
Пример моего кода на состояние марта 2025 года. Это НЕ финальная версия, отстает примерно на 6 месяцев (напишите мне если нужен форк). Для запуска потребуется пакет "rubik_core" - это логика ядра сервиса, его можно написать самому или связаться со мной. Код выложен в демонстрационных целях и не предназначен для запуска. 

# Dating service based on shared likes An example of my code as of March 2025. 
This is NOT the final version, missed 6 mothn approximately, (please contact me if you need a fork). To run it, you will need the "rubik_core" package - this is the core logic of the service, which you can write yourself or contact me for. The code is published for demonstration purposes only and is not intended for actual deployment.

```
david@david-ThinkPad-E480:~/PycharmProjects$ scc rubik_tg_bot/
───────────────────────────────────────────────────────────────────────────────
Language                 Files     Lines   Blanks  Comments     Code Complexity
───────────────────────────────────────────────────────────────────────────────
Python                     161     24747     2765      2314    19668        825
JSON                        54       397       30         0      367          0
Plain Text                  19       196        9         0      187          0
Markdown                     6       481      104         0      377          0
Shell                        3        41        6         4       31          4
Systemd                      1        13        3         0       10          0
YAML                         1        72        6         8       58          0
gitignore                    1        17        2         1       14          0
───────────────────────────────────────────────────────────────────────────────
Total                      246     25964     2925      2327    20712        829
───────────────────────────────────────────────────────────────────────────────
Estimated Cost to Develop (organic) $651,071
Estimated Schedule Effort (organic) 11.68 months
Estimated People Required (organic) 4.95
───────────────────────────────────────────────────────────────────────────────
Processed 1058483 bytes, 1.058 megabytes (SI)
───────────────────────────────────────────────────────────────────────────────

david@david-ThinkPad-E480:~/PycharmProjects$ scc rubik_core
───────────────────────────────────────────────────────────────────────────────
Language                 Files     Lines   Blanks  Comments     Code Complexity
───────────────────────────────────────────────────────────────────────────────
Python                      53      7018      713       280     6025        310
XML                         17       280        0         0      280          0
gitignore                    3         8        0         3        5          0
SQL                          2       260       46         0      214          0
TOML                         1        17        3         0       14          1
───────────────────────────────────────────────────────────────────────────────
Total                       76      7583      762       283     6538        311
───────────────────────────────────────────────────────────────────────────────
Estimated Cost to Develop (organic) $194,004
Estimated Schedule Effort (organic) 7.38 months
Estimated People Required (organic) 2.34
───────────────────────────────────────────────────────────────────────────────
Processed 271731 bytes, 0.272 megabytes (SI)
───────────────────────────────────────────────────────────────────────────────

david@david-ThinkPad-E480:~/PycharmProjects$ scc RubikLoveMobile/
───────────────────────────────────────────────────────────────────────────────
Language                 Files     Lines   Blanks  Comments     Code Complexity
───────────────────────────────────────────────────────────────────────────────
TypeScript                  88      5946      273       275     5398         83
SVG                         53       600        0         0      600          0
JSON                         4       150        2         0      148          0
JavaScript                   3        67        4         0       63          0
TypeScript Typings           1         8        1         1        6          0
gitignore                    1        17        2         2       13          0
───────────────────────────────────────────────────────────────────────────────
Total                      150      6788      282       278     6228         83
───────────────────────────────────────────────────────────────────────────────
Estimated Cost to Develop (organic) $184,357
Estimated Schedule Effort (organic) 7.23 months
Estimated People Required (organic) 2.26
───────────────────────────────────────────────────────────────────────────────
Processed 368456 bytes, 0.368 megabytes (SI)
───────────────────────────────────────────────────────────────────────────────

david@david-ThinkPad-E480:~/PycharmProjects$ scc --version
scc version 3.1.0
david@david-ThinkPad-E480:~/PycharmProjects$ 
```
