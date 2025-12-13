/* Lightweight React typings workaround for environments without @types/react.
   We declare a global React to satisfy the TS compiler in this sandbox. */
declare var React: any;

// データの1行を表す型定義。実際のプロジェクトでは項目を適宜拡張してください。
type DataRow = {
  id: string;
  name: string;
  value: string;
  // ... 他のフィールド
};

type Props = {
  data: DataRow[];
  onUpdate: (rows: DataRow[]) => void;
};

export const DataInputTab = ({ data, onUpdate }: Props) => {
  // 編集状態を管理
  const [editingId, setEditingId] = React.useState(null);
  const [editRow, setEditRow] = React.useState(null);

  const startEdit = (row: DataRow) => {
    setEditingId(row.id);
    setEditRow({ ...row });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditRow(null);
  };

  const onChange = (field: keyof DataRow, value: string) => {
    if (!editRow) return;
    setEditRow({ ...editRow, [field]: value });
  };

  const saveEdit = async () => {
    if (!editRow || !editingId) return;
    // 最小のエラーハンドリング
    try {
      const updated = await fetch(`/api/data/${editingId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editRow),
      }).then(res => {
        if (!res.ok) {
          throw new Error(`Request failed with status ${res.status}`);
        }
        return res.json();
      });

      const next = data.map(d => (d.id === updated.id ? updated : d));
      onUpdate(next);
      setEditingId(null);
      setEditRow(null);
    } catch (err) {
      // 本番環境ではトースト通知等のUXを追加してください
      console.error('データ編集の保存に失敗しました', err);
    }
  };

  return (
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
        {data.map(row => {
          const isEditing = editingId === row.id;
          return (
            <tr key={row.id}>
              {isEditing ? (
                <>
                  <td>{row.id}</td>
                  <td>
                    <input
                      value={editRow?.name ?? ''}
                      onChange={e => onChange('name', e.target.value)}
                    />
                  </td>
                  <td>
                    <input
                      value={editRow?.value ?? ''}
                      onChange={e => onChange('value', e.target.value)}
                    />
                  </td>
                  <td>
                    <button onClick={saveEdit}>Save</button>
                    <button onClick={cancelEdit}>Cancel</button>
                  </td>
                </>
              ) : (
                <>
                  <td>{row.id}</td>
                  <td>{row.name}</td>
                  <td>{row.value}</td>
                  <td>
                    <button onClick={() => startEdit(row)}>Edit</button>
                  </td>
                </>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default DataInputTab;


