import os
import re

files_to_fix = [
    r"c:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src\services\brain_learning_service.py",
    r"c:\Users\preio\OneDrive\Documents\Untitled\perplex_engine\perplex-edge\apps\api\src\services\brain_system_state_service.py"
]

def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add sqlalchemy imports at the top
    if "from sqlalchemy import text" not in content:
        content = content.replace("import asyncpg", "import asyncpg\nfrom sqlalchemy import text\nfrom database import async_session_maker")

    # Fix get_system_performance query mappings
    # result = await conn.fetchrow(...) -> res = await conn.execute(text(...)); row = res.mappings().first()
    
    # Let's do a complete manual rewrite for each block type:
    
    # 1. conn = await asyncpg.connect(self.db_url)
    content = content.replace("conn = await asyncpg.connect(self.db_url)", "conn_ctx = async_session_maker(); conn = await conn_ctx.__aenter__()")
    content = content.replace("await conn.close()", "await conn.commit(); await conn_ctx.__aexit__(None, None, None)")
    
    # 2. execute updates with values
    # await conn.execute("... VALUES ($1, $2)", v1, v2) -> await conn.execute(text("... VALUES (:p1, :p2)"), {"p1":v1, "p2":v2})
    
    def repl_execute(m):
        query = m.group(1)
        args_str = m.group(2)
        # convert $1 to :p1
        query = re.sub(r'\$(\d+)', r':p\1', query)
        
        # build dict
        if args_str.strip():
            args = [a.strip() for a in args_str.split(',') if a.strip()]
            dict_str = "{" + ", ".join(f'"p{i+1}": {arg}' for i, arg in enumerate(args)) + "}"
            return f'await conn.execute(text({query}), {dict_str})'
        else:
            return f'await conn.execute(text({query}))'

    content = re.sub(r'await conn\.execute\((["\'].*?["\'])(?:,\s*(.*?))?\)', repl_execute, content, flags=re.DOTALL)
    
    # 3. fetchrow
    def repl_fetchrow(m):
        query = m.group(1)
        args_str = m.group(2)
        query = re.sub(r'\$(\d+)', r':p\1', query)
        
        # also fix interval logic
        query = query.replace("INTERVAL ':hours hours'", "INTERVAL '1 hour' * :p1").replace("INTERVAL '$1 hours'", "INTERVAL '1 hour' * :p1")
        
        if args_str and args_str.strip():
            args = [a.strip() for a in args_str.split(',') if a.strip()]
            dict_str = "{" + ", ".join(f'"p{i+1}": {arg}' for i, arg in enumerate(args)) + "}"
            return f'(await conn.execute(text({query}), {dict_str})).mappings().first()'
        else:
            return f'(await conn.execute(text({query}))).mappings().first()'

    content = re.sub(r'await conn\.fetchrow\((["\']{3}.*?["\']{3}|["\'].*?["\'])(?:,\s*(.*?))?\)', repl_fetchrow, content, flags=re.DOTALL)
    
    # 4. fetch
    def repl_fetch(m):
        query = m.group(1)
        args_str = m.group(2)
        query = re.sub(r'\$(\d+)', r':p\1', query)
        query = query.replace("INTERVAL ':hours hours'", "INTERVAL '1 hour' * :p1").replace("INTERVAL '$1 hours'", "INTERVAL '1 hour' * :p1")
        
        if args_str and args_str.strip():
            args = [a.strip() for a in args_str.split(',') if a.strip()]
            dict_str = "{" + ", ".join(f'"p{i+1}": {arg}' for i, arg in enumerate(args)) + "}"
            return f'(await conn.execute(text({query}), {dict_str})).mappings().all()'
        else:
            return f'(await conn.execute(text({query}))).mappings().all()'

    content = re.sub(r'await conn\.fetch\((["\']{3}.*?["\']{3}|["\'].*?["\'])(?:,\s*(.*?))?\)', repl_fetch, content, flags=re.DOTALL)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

for f in files_to_fix:
    fix_file(f)
print("done")
