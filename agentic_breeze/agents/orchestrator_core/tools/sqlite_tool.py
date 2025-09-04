import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any, Tuple, Union
import os

# 定義 SQLite 支援的資料類型
SQLiteType = Literal["TEXT", "INTEGER", "REAL", "BLOB", "NUMERIC"]

@dataclass
class ColumnDefinition:
    """定義資料表中的一個欄位。"""
    name: str
    dtype: SQLiteType
    nullable: bool = True
    is_primary_key: bool = False
    is_unique: bool = False
    default: Optional[str] = None
    description: Optional[str] = None

@dataclass
class TableDefinition:
    """定義一個資料表的 schema。"""
    name: str
    columns: List[ColumnDefinition]
    description: Optional[str] = None
    # 未來可以考慮添加 indexes: List[IndexDefinition] 等更複雜的定義


class SQLiteSchemaTool:
    """
    一個用於管理 SQLite 資料庫 schema 和執行查詢的工具。
    """
    def __init__(self, db_path: str = "sample_users.db"):
        self._db_path = db_path

    def _table_exists(self, cursor: sqlite3.Cursor, table_name: str) -> bool:
        """檢查資料表是否存在。"""
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return cursor.fetchone() is not None

    def _get_existing_columns(self, cursor: sqlite3.Cursor, table_name: str) -> Dict[str, Dict[str, Any]]:
        """獲取現有資料表的欄位資訊。"""
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns_info = {}
        for row in cursor.fetchall():
            columns_info[row['name']] = {
                "name": row['name'],
                "type": row['type'],
                "notnull": bool(row['notnull']),
                "pk": bool(row['pk']),
                "dflt_value": row['dflt_value']
            }
        return columns_info

    def _generate_create_table_ddl(self, table_definition: TableDefinition) -> str:
        """根據 TableDefinition 生成 CREATE TABLE 語句。"""
        columns_sql = []
        primary_keys = []
        for col in table_definition.columns:
            col_sql = f"{col.name} {col.dtype}"
            if not col.nullable:
                col_sql += " NOT NULL"
            if col.is_unique:
                col_sql += " UNIQUE"
            if col.default is not None:
                # 確保預設值格式正確，例如字串需要單引號
                if col.dtype == "TEXT":
                    col_sql += f" DEFAULT '{col.default}'"
                else:
                    col_sql += f" DEFAULT {col.default}"
            if col.is_primary_key:
                primary_keys.append(col.name)
            columns_sql.append(col_sql)

        if primary_keys:
            columns_sql.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

        return f"CREATE TABLE {table_definition.name} ({', '.join(columns_sql)})"

    def _generate_migrate_ddl(self, table_definition: TableDefinition,
                              existing_columns: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        比對 schema 並生成非破壞性 ALTER TABLE 語句（追加欄位和索引）。
        """
        ddl_statements = []
        for new_col in table_definition.columns:
            if new_col.name not in existing_columns:
                # 追加新欄位
                col_sql = f"{new_col.name} {new_col.dtype}"
                if not new_col.nullable:
                    col_sql += " NOT NULL"
                if new_col.is_unique:
                    col_sql += " UNIQUE"
                if new_col.default is not None:
                    if new_col.dtype == "TEXT":
                        col_sql += f" DEFAULT '{new_col.default}'"
                    else:
                        col_sql += f" DEFAULT {new_col.default}"
                ddl_statements.append(f"ALTER TABLE {table_definition.name} ADD COLUMN {col_sql}")
            # 簡化處理：對於現有欄位，不允許更改類型或刪除，避免數據破壞

        # 這裡可以添加索引的處理邏輯，例如為 is_unique 和 is_primary_key 的欄位自動創建索引
        # 或者支援 TableDefinition 中明確定義的索引
        return ddl_statements

    def define_table(self, table_definition: TableDefinition) -> Dict[str, Any]:
        """
        根據 dataclass 定義的 schema 遷移資料表。
        支持非破壞性遷移（追加欄位）。不允許創建新表。
        """
        try:
            # 在嘗試獲取連接之前，先檢查資料庫檔案是否存在。
            # 如果檔案不存在，則直接返回錯誤，因為設定LLM 無法創建新的資料庫檔案。
            if not os.path.exists(self._db_path):
                return {"status": "error", "message": f"Database file '{self._db_path}' does not exist. New table creation is not allowed.", "error_details": "Database file not found and creation disallowed"}

            with sqlite3.connect(self._db_path, timeout=30) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                table_name = table_definition.name

                if not self._table_exists(cursor, table_name):
                    return {"status": "error", "message": f"Table '{table_name}' does not exist. New table creation is not allowed.", "error_details": "Table not found and creation disallowed"}
                else:
                    # 資料表已存在，比對並遷移
                    existing_columns = self._get_existing_columns(cursor, table_name)
                    ddl_statements = self._generate_migrate_ddl(table_definition, existing_columns)
                    if ddl_statements:
                        for ddl in ddl_statements:
                            cursor.execute(ddl)
                        conn.commit()
                        return {"status": "success", "message": f"Table '{table_name}' migrated successfully. Added {len(ddl_statements)} new columns."}
                    else:
                        return {"status": "success", "message": f"Table '{table_name}' schema is up to date."}

        except sqlite3.Error as e:
            # with 語句會自動處理連接關閉，這裡只需處理回滾
            return {"status": "error", "message": f"Failed to define/migrate table '{table_name}': {e}", "error_details": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred during table definition: {e}", "error_details": str(e)}

    def query_to_dicts(self, sql_query: str, params: Optional[Union[Tuple, Dict]] = None) -> Dict[str, Any]:
        """
        執行 SELECT 語句並回傳結果為字典列表。
        """
        try:
            with sqlite3.connect(self._db_path, timeout=30) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if params:
                    cursor.execute(sql_query, params)
                else:
                    cursor.execute(sql_query)
                
                rows = cursor.fetchall()
                # sqlite3.Row 已經讓結果可以像字典一樣訪問
                results = [dict(row) for row in rows]
                
                return {"status": "success", "data": results, "row_count": len(results)}
        except sqlite3.Error as e:
            return {"status": "error", "message": f"Failed to query data: {e}", "error_details": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred during data query: {e}", "error_details": str(e)}

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        獲取指定資料表的詳細資訊，包括欄位、型別等。
        """
        try:
            with sqlite3.connect(self._db_path, timeout=30) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if not self._table_exists(cursor, table_name):
                    return {"status": "error", "message": f"Table '{table_name}' does not exist.", "error_details": "Table not found"}

                columns_info = self._get_existing_columns(cursor, table_name)
                
                return {"status": "success", "table_name": table_name, "columns": columns_info}
        except sqlite3.Error as e:
            return {"status": "error", "message": f"Failed to get table info: {e}", "error_details": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred while getting table info: {e}", "error_details": str(e)}