import re

with open('data/raw/sansovi_salary_benchmark.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="f-role"')
print('f-role index:', idx)
if idx != -1:
    start = html.rfind('<section', 0, idx)
    end = html.find('</section>', idx) + 10
    with open('data/raw/sansovi_section.html', 'w', encoding='utf-8') as sf:
        sf.write(html[start:end])
    print('Saved extracted section, length:', end - start)
