"""Compile and execute actual C programs; preserve byte-exact stdout/stderr."""
import argparse, hashlib, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent

def run(task):
    folder = ROOT / task
    (ROOT / 'build').mkdir(exist_ok=True)
    (folder / 'outputs').mkdir(exist_ok=True)
    manifest = []
    for source in sorted(folder.glob('*.c')):
        name = source.stem
        flags = ['-std=c11', '-Wall'] + ([] if name == 'ub_demo' else ['-Wextra'])
        cmd = ['gcc', *flags, f'{task}/{source.name}', '-o', f'build/{task}_{name}.exe']
        if '#include <math.h>' in source.read_text(): cmd += ['-lm']
        comp = subprocess.run(cmd, cwd=ROOT, capture_output=True)
        (folder/'outputs'/f'{name}.compiler.txt').write_bytes(comp.stdout + comp.stderr)
        if comp.returncode: raise RuntimeError(comp.stderr.decode(errors='replace'))
        if name != 'ub_demo' and comp.stderr: raise RuntimeError('Unexpected compiler diagnostic: '+comp.stderr.decode())
        if name == 'ub_demo' and b'-Wsequence-point' not in comp.stderr: raise AssertionError('Expected actual UB warning')
        data = (folder/'inputs'/f'{name}.txt').read_bytes()
        execution = subprocess.run([str(ROOT/cmd[-1 if cmd[-1]!='-lm' else -2])], input=data, capture_output=True, cwd=ROOT, timeout=60)
        if execution.returncode: raise RuntimeError(execution.stderr.decode(errors='replace'))
        (folder/'outputs'/f'{name}.stdout.txt').write_bytes(execution.stdout)
        (folder/'outputs'/f'{name}.stderr.txt').write_bytes(execution.stderr)
        transcript = '$ ' + subprocess.list2cmdline(cmd) + '\n' + comp.stdout.decode(errors='replace') + comp.stderr.decode(errors='replace')
        transcript += '$ ' + f'build/{task}_{name}.exe < {task}/inputs/{name}.txt\n' + execution.stdout.decode(errors='replace') + execution.stderr.decode(errors='replace')
        (folder/'outputs'/f'{name}.transcript.txt').write_text(transcript, encoding='utf-8')
        expected = folder/'expected'/f'{name}.txt'
        if expected.exists():
            assert execution.stdout == expected.read_bytes(), f'{task}/{name}: byte mismatch'
        manifest.append(dict(source=source.name, command=cmd, exit_code=execution.returncode, stdout_sha256=hashlib.sha256(execution.stdout).hexdigest(), expected_bytes_match=expected.exists()))
        print(f'{task}/{name}: compiled and executed; {len(execution.stdout)} stdout bytes')
    (folder/'outputs'/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('tasks', nargs='*', default=[f'Q{i}' for i in range(1,8)])
    for task in p.parse_args().tasks: run(task)
