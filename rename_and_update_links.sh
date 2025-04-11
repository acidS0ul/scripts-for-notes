#!/bin/bash

for file in *; do
    if [[ ! -f "$file" ]]; then
        continue
    fi

    new_name=$(echo "$file" | tr ' ' '_')

    if [[ "$file" != "$new_name" ]]; then
        mv -- "$file" "$new_name"
        echo "Переименован: '$file' → '$new_name'"
        find . -type f -exec sed -i "s/$file/$new_name/g" {} +   
    fi
done

echo "Готово!"
