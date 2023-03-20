from pattern.text.es import pluralize as pluralize_es
from pattern.text.en import pluralize as pluralize_en

word1 = "application"
word2 = "component"

palabra1 = "aplicación"
palabra2 = "componente"

print("English word")
print("Singular: " + word1)
print("Plural: " + pluralize_en(word1))

print("\nPalabra en español")
print("Singular: " + palabra1)
print("Plural: " + pluralize_es(palabra1))

