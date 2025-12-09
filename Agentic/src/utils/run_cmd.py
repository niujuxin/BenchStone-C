
from pathlib import Path
import re
import shutil
import asyncio
import subprocess
from typing import Dict, Optional, Union
from dataclasses import dataclass


def checkexe(exe: str, *, raise_on_error: bool = True):
    exist = shutil.which(exe)
    if not exist and raise_on_error:
        raise FileNotFoundError(f"{exe} is not found in PATH. Please install {exe}.")
    return exist


def checkexes(exes: list, *, raise_on_error: bool = True):
    for exe in exes:
        checkexe(exe, raise_on_error=raise_on_error)


@dataclass(frozen=True)
class CommandExecResult:
    return_code: int
    stdout: str
    stderr: str

    @property
    def is_ok(self):
        return self.return_code == 0

    def to_json(self) -> dict:
        return {
            'return_code': self.return_code,
            'stdout': self.stdout,
            'stderr': self.stderr,
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'CommandExecResult':
        return cls(
            return_code=data['return_code'],
            stdout=data['stdout'],
            stderr=data['stderr'],
        )


class CommandRunner:
    """
    A unified class for running commands both synchronously and asynchronously,
    with ANSI escape sequence removal.
    """
    
    _ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    
    @classmethod
    def _prepare_command(cls, command: Union[str, list], use_shell: bool) -> Union[str, list]:
        """
        Prepares the command for execution based on shell usage.
        """
        if use_shell:
            # Shell expects a string
            if isinstance(command, list):
                return ' '.join(command)
            return command
        else:
            # Non-shell expects a list
            if isinstance(command, str):
                return command.split()
            return command
    
    @classmethod
    def _clean_output(cls, text: str) -> str:
        """
        Removes ANSI escape sequences from text.
        """
        return cls._ansi_escape.sub('', text if text else '')
    
    @classmethod
    def run(
        cls,
        command: Union[str, list],
        *,
        workingdir: Optional[str | Path] = None,
        raise_on_error: bool = False,
        io_encoding: str = 'utf-8',
        use_shell: bool = False,
        env: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> CommandExecResult:
        """
        Runs a command synchronously and returns CommandExecResult instance, 
        with ANSI escape sequences removed. Optionally raises an exception if
        the return code is not zero.

        Args:
            command: Command to be executed. Can be a string or list of strings.
            workingdir: Working directory where the command should be executed.
            raise_on_error: If True, will raise CalledProcessError when the command 
                returns a non-zero status (default: False).
            io_encoding: Encoding used to decode stdout and stderr (default: 'utf-8').
            use_shell: If True, the command will be executed in a shell 
                (e.g., /bin/sh on Unix) (default: False).
            env: Dictionary for the child process's environment variables (default: None).
            timeout: Timeout in seconds; if exceeded, a TimeoutExpired exception is raised (default: None).

        Returns:
            An instance of CommandExecResult for the command executed.

        Raises:
            subprocess.CalledProcessError: If raise_on_error is True and the command 
                exits with a non-zero return code.
            subprocess.TimeoutExpired: If the command does not complete before the 
                timeout duration.
        """
        prepared_command = cls._prepare_command(command, use_shell)

        if workingdir is not None:
            workingdir = Path(workingdir).as_posix()

        result = subprocess.run(
            prepared_command,
            cwd=workingdir,
            check=raise_on_error,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=use_shell,
            env=env,
            encoding=io_encoding,
            timeout=timeout,
            errors='replace'  # Replace decoding errors with a placeholder character
        )
        
        # Clean out ANSI escape sequences from stdout/stderr
        stdout_clean = cls._clean_output(result.stdout)
        stderr_clean = cls._clean_output(result.stderr)

        return CommandExecResult(
            return_code=result.returncode,
            stdout=stdout_clean,
            stderr=stderr_clean
        )
    
    @classmethod
    async def run_async(
        cls,
        command: Union[str, list],
        *,
        workingdir: Optional[str] = None,
        raise_on_error: bool = False,
        io_encoding: str = 'utf-8',
        use_shell: bool = False,
        env: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> CommandExecResult:
        """
        Runs a command asynchronously and returns CommandExecResult instance, 
        with ANSI escape sequences removed. Optionally raises an exception if
        the return code is not zero.

        Args:
            command: Command to be executed. Can be a string or list of strings.
            workingdir: Working directory where the command should be executed.
            raise_on_error: If True, will raise CalledProcessError when the command 
                returns a non-zero status (default: False).
            io_encoding: Encoding used to decode stdout and stderr (default: 'utf-8').
            use_shell: If True, the command will be executed in a shell 
                (e.g., /bin/sh on Unix) (default: False).
            env: Dictionary for the child process's environment variables (default: None).
            timeout: Timeout in seconds; if exceeded, a TimeoutExpired exception is raised (default: None).

        Returns:
            An instance of CommandExecResult for the command executed.

        Raises:
            subprocess.CalledProcessError: If raise_on_error is True and the command 
                exits with a non-zero return code.
            asyncio.TimeoutError: If the command does not complete before the 
                timeout duration.
        """
        # Prepare the command for create_subprocess_exec or create_subprocess_shell
        if use_shell:
            command_str = cls._prepare_command(command, use_shell=True)
            proc = await asyncio.create_subprocess_shell(
                command_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workingdir,
                env=env,
            )
        else:
            command_list = cls._prepare_command(command, use_shell=False)
            proc = await asyncio.create_subprocess_exec(
                *command_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workingdir,
                env=env,
            )

        try:
            # Wait for the process to complete with optional timeout
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            # Kill the process if it times out
            proc.kill()
            await proc.wait()
            raise

        # Decode the output
        stdout = stdout_bytes.decode(io_encoding) if stdout_bytes else ''
        stderr = stderr_bytes.decode(io_encoding) if stderr_bytes else ''

        # Clean out ANSI escape sequences from stdout/stderr
        stdout_clean = cls._clean_output(stdout)
        stderr_clean = cls._clean_output(stderr)

        # Check if we need to raise an error for non-zero return code
        if raise_on_error and proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode,
                command,
                output=stdout_clean,
                stderr=stderr_clean
            )

        return CommandExecResult(
            return_code=proc.returncode,
            stdout=stdout_clean,
            stderr=stderr_clean
        )
