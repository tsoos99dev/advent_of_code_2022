from dataclasses import dataclass, field
from typing import Protocol, Callable, Optional, Iterable

from calendar.calendar import Calendar


@dataclass
class DirectoryNotFoundError(Exception):
    name: str

    def __str__(self):
        return f"'{self.name}' is not a directory"


class FileSystemObject(Protocol):
    name: str

    def get_size(self) -> int:
        ...


@dataclass
class File:
    name: str
    size: int

    def get_size(self) -> int:
        return self.size


@dataclass
class Directory:
    name: str
    parent: Optional['Directory'] = field(default=None)
    contents: dict[str, FileSystemObject] = field(default_factory=dict)

    def get_size(self):
        return sum(content.get_size() for content in self.contents.values())


class FileSystemCommand(Protocol):
    def execute(self, current_directory: Directory, set_current_directory: Callable[[Directory], None]) -> Optional[Iterable[FileSystemObject]]:
        ...


@dataclass
class FileSystem:
    root: Directory = field(default_factory=lambda: Directory('/'))

    def __post_init__(self):
        self.current_directory = self.root

    def execute_command(self, command: FileSystemCommand):
        def set_current_directory(directory: Directory):
            self.current_directory = directory

        return command.execute(self.current_directory, set_current_directory)


@dataclass
class EnterDirectory:
    destination: str

    def execute(self, current_directory: Directory, set_current_directory: Callable[[Directory], None]) -> Optional[Iterable[FileSystemObject]]:
        destination_directory = current_directory.contents.get(self.destination, None)
        if destination_directory is None:
            raise DirectoryNotFoundError(self.destination)

        if not isinstance(destination_directory, Directory):
            raise DirectoryNotFoundError(self.destination)

        set_current_directory(destination_directory)
        return None


@dataclass
class EnterRootDirectory:
    def execute(self, current_directory: Directory, set_current_directory: Callable[[Directory], None]) -> Optional[Iterable[FileSystemObject]]:
        destination_directory = current_directory
        while parent := destination_directory.parent:
            destination_directory = parent

        set_current_directory(destination_directory)
        return None


@dataclass
class LeaveDirectory:
    def execute(self, current_directory: Directory, set_current_directory: Callable[[Directory], None]) -> Optional[Iterable[FileSystemObject]]:
        destination_directory = current_directory.parent
        set_current_directory(destination_directory or current_directory)
        return None


@dataclass
class ListDirectory:
    def execute(self, current_directory: Directory, _: Callable[[Directory], None]) -> Optional[Iterable[FileSystemObject]]:
        return iter(current_directory.contents.values())


@dataclass
class CreateFile:
    name: str
    size: int

    def execute(self, current_directory: Directory, _: Callable[[Directory], None]) -> Optional[Iterable[FileSystemObject]]:
        current_directory.contents[self.name] = File(self.name, self.size)
        return None


@dataclass
class CreateDirectory:
    name: str

    def execute(self, current_directory: Directory, _: Callable[[Directory], None]) -> Optional[Iterable[FileSystemObject]]:
        current_directory.contents[self.name] = Directory(self.name, parent=current_directory)
        return None


@Calendar.register(day=7)
@dataclass
class Solution:
    puzzle_input: str

    def __post_init__(self):
        self.file_system = FileSystem()
        command_list = self.puzzle_input.splitlines()

        for command_input in command_list:
            command = self.parse_command(command_input)
            if command is None:
                continue

            try:
                self.file_system.execute_command(command)
            except DirectoryNotFoundError as e:
                self.file_system.execute_command(CreateDirectory(e.name))

        self.file_system.execute_command(EnterRootDirectory())
        self.directories = self.list_all_directories()

    @staticmethod
    def parse_command(command_input: str) -> Optional[FileSystemCommand]:
        match command_input.split(' '):
            case ['$', 'cd', '/']:
                return EnterRootDirectory()
            case ['$', 'cd', '..']:
                return LeaveDirectory()
            case ['$', 'cd', name]:
                return EnterDirectory(name)
            case ['$', 'ls']:
                return None
            case ['dir', name]:
                return CreateDirectory(name)
            case [size, name]:
                return CreateFile(name, int(size))

        return None

    def list_all_directories(self, directories=None):
        if directories is None:
            directories = []

        for content in self.file_system.execute_command(ListDirectory()):
            try:
                self.file_system.execute_command(EnterDirectory(content.name))
                directories = self.list_all_directories(directories)
                self.file_system.execute_command(LeaveDirectory())
            except DirectoryNotFoundError:
                continue

        directories.append(self.file_system.current_directory)
        return directories

    def part1(self):
        return sum(directory_size for directory in self.directories if (directory_size := directory.get_size()) <= 100000)

    def part2(self):
        current_size = self.file_system.root.get_size()
        space_to_be_freed = current_size + 30000000 - 70000000
        candidates = filter(lambda directory: directory.get_size() >= space_to_be_freed, self.directories)
        return sorted(candidates, key=lambda directory: directory.get_size())[0].get_size()


