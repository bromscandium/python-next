"use client";

import { useState } from "react";

export default function CatForm({ onCreate, disabled }) {
    const [form, setForm] = useState({
        name: "",
        years_of_experience: "",
        breed: "",
        salary: "",
    });

    async function submit(e) {
        e.preventDefault();
        await onCreate({
            name: form.name.trim(),
            years_of_experience: Number(form.years_of_experience),
            breed: form.breed.trim(),
            salary: Number(form.salary),
        });
        setForm({ name: "", years_of_experience: "", breed: "", salary: "" });
    }

    return (
        <form onSubmit={submit} className="grid">
            <label>
                <span>Name</span>
                <input
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    required
                    maxLength={120}
                />
            </label>
            <label>
                <span>Years of experience</span>
                <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.years_of_experience}
                    onChange={(e) =>
                        setForm({ ...form, years_of_experience: e.target.value })
                    }
                    required
                />
            </label>
            <label>
                <span>Breed</span>
                <input
                    value={form.breed}
                    onChange={(e) => setForm({ ...form, breed: e.target.value })}
                    placeholder="e.g. beng or Bengal"
                    required
                />
            </label>
            <label>
                <span>Salary</span>
                <input
                    type="number"
                    min="0"
                    step="1"
                    value={form.salary}
                    onChange={(e) => setForm({ ...form, salary: e.target.value })}
                    required
                />
            </label>
            <div className="actions">
                <button disabled={disabled}>Create</button>
            </div>
        </form>
    );
}
