import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { DataInputTab } from '../../src/components/DataInputTab';

describe('DataInputTab インライン編集 - 統合テスト雛形', () => {
  const mockInitialData = [
    { id: '1', name: 'Alpha', value: '01' },
    { id: '2', name: 'Beta', value: '02' },
  ];

  beforeEach(() => {
    // ダミーの PATCH レスポンスを返却
    (global as any).fetch = jest.fn().mockImplementation((url: string, opts: any) => {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          id: url.split('/').pop(),
          name: opts.body ? JSON.parse(opts.body).name : 'Updated',
          value: opts.body ? JSON.parse(opts.body).value : 'Updated',
        }),
      });
    });
  });

  test('Edit -> name/value を更新して Save すると onUpdate が呼ばれる', async () => {
    const onUpdate = jest.fn();
    const { getByText, getByDisplayValue } = render(
      <DataInputTab initialData={mockInitialData} onUpdate={onUpdate} />
    );

    // 1行目を編集モードへ
    fireEvent.click(getByText('Edit'));

    // Name/value を変更
    const nameInput = getByDisplayValue('Alpha');
    fireEvent.change(nameInput, { target: { value: 'AlphaEdited' } });
    const valueInput = getByDisplayValue('01');
    fireEvent.change(valueInput, { target: { value: '01-edited' } });

    // Save をクリック
    fireEvent.click(getByText('Save'));

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalled();
    });
  });

  test('Cancel を押すと編集モードが終了する', async () => {
    const onUpdate = jest.fn();
    const { getByText, getByRole, queryByRole } = render(
      <DataInputTab initialData={mockInitialData} onUpdate={onUpdate} />
    );

    // 1行目を編集モードへ
    fireEvent.click(getByText('Edit'));

    // Cancel をクリック
    fireEvent.click(getByText('Cancel'));

    // 編集モードが終了して元に戻るかを確認
    expect(queryByRole('textbox')).toBeNull();
  });
});


