from pprint import pprint

def main():
    with open('input.txt', encoding='utf-8') as file:
        elf_inventories = file.read().split("\n\n")
        total_calories = [
            sum(
                int(calorie_str)
                for calorie_str in inventory.split('\n')
                if calorie_str != ''
            )
            for inventory in elf_inventories]

        # Part 1
        print(max(total_calories))

        # Part 2
        print(sum(sorted(total_calories, reverse=True)[:3]))


if __name__ == '__main__':
    main()