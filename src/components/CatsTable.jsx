"use client";

import CatRow from "./CatRow";

export default function CatsTable({ cats, loading, onUpdateSalary, onDelete }) {
    if (loading) return <div>Loading…</div>;
    if (!cats?.length) return <div>No cats yet</div>;

    return (
        <table className="table">
            <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>YoE</th>
                <th>Breed</th>
                <th>Salary</th>
                <th></th>
            </tr>
            </thead>
            <tbody>
            {cats.map((c) => (
                <CatRow
                    key={c.id}
                    cat={c}
                    onUpdateSalary={onUpdateSalary}
                    onDelete={onDelete}
                />
            ))}
            </tbody>
        </table>
    );
}
