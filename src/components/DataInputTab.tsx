declare var React: any;

type DataRow = {
  id: string | number;
  name: string;
  value: string;
  // 追加フィールドがあればここに定義
};

type DataInputTabProps = {
  initialData?: DataRow[];
  data?: DataRow[];
  onUpdate?: (rows: DataRow[]) => void;
};

export const DataInputTab = ({ initialData, data, onUpdate }: DataInputTabProps) => {
  const [rows, setRows] = React.useState([] as DataRow[]);
  const [editingId, setEditingId] = React.useState(null as string | number | null);
  const [editRow, setEditRow] = React.useState(null as DataRow | null);
  const [error, setError] = React.useState(null as string | null);

  // 外部データ変更に追従
  React.useEffect(() => {
    const source = data ?? initialData ?? [];
    setRows(source);
  }, [data, initialData]);

  const startEdit = (row: DataRow) => {
    setEditingId(row.id);
    setEditRow({ ...row });
    setError(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditRow(null);
    setError(null);
  };

  const onChangeEdit = (field: keyof DataRow, value: string) => {
    if (!editRow) return;
    setEditRow({ ...editRow, [field]: value });
  };

  const saveEdit = async () => {
    if (!editRow || editingId == null) return;
    try {
      const resp = await fetch(`/api/data/${editingId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editRow),
      });
      if (!resp.ok) {
        throw new Error(`Update failed: ${resp.status} ${resp.statusText}`);
      }
      const updated: DataRow = await resp.json();
      const nextRows = rows.map((r) => (r.id === updated.id ? updated : r));
      setRows(nextRows);
      if (onUpdate) onUpdate(nextRows);
      cancelEdit();
    } catch (err) {
      console.error(err);
      setError('データの更新に失敗しました');
    }
  };

  return (
    <div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Value</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const isEditing = editingId === row.id;
            return (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>
                  {isEditing ? (
                    <input
                      value={editRow?.name ?? ''}
                      onChange={(e) => onChangeEdit('name', e.target.value)}
                    />
                  ) : (
                    row.name
                  )}
                </td>
                <td>
                  {isEditing ? (
                    <input
                      value={editRow?.value ?? ''}
                      onChange={(e) => onChangeEdit('value', e.target.value)}
                    />
                  ) : (
                    row.value
                  )}
                </td>
                <td>
                  {isEditing ? (
                    <>
                      <button onClick={saveEdit}>Save</button>
                      <button onClick={cancelEdit}>Cancel</button>
                    </>
                  ) : (
                    <button onClick={() => startEdit(row)}>Edit</button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default DataInputTab;
