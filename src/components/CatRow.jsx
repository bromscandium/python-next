"use client";

import { useState } from "react";

export default function CatRow({ cat, onUpdateSalary, onDelete }) {
    const [edit, setEdit] = useState(false);
    const [val, setVal] = useState(cat.salary);
    const [saving, setSaving] = useState(false);

    async function save() {
        setSaving(true);
        await onUpdateSalary(cat.id, Number(val));
        setSaving(false);
        setEdit(false);
    }

    return (
        <tr>
            <td>{cat.id}</td>
            <td>{cat.name}</td>
            <td>{cat.years_of_experience}</td>
            <td>{cat.breed}</td>
            <td>
                {edit ? (
                    <span className="inline-edit">
            <input
                type="number"
                min="0"
                step="1"
                value={val}
                onChange={(e) => setVal(e.target.value)}
            />
            <button onClick={save} disabled={saving}>
              Save
            </button>
            <button
                className="ghost"
                onClick={() => {
                    setEdit(false);
                    setVal(cat.salary);
                }}
            >
              Cancel
            </button>
          </span>
                ) : (
                    <span>{cat.salary}</span>
                )}
            </td>
            <td className="right">
                {!edit && <button onClick={() => setEdit(true)}>Edit</button>}
                <button className="danger" onClick={() => onDelete(cat.id)}>
                    Delete
                </button>
            </td>
        </tr>
    );
}
