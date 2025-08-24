"use client";

import { useEffect, useState } from "react";
import { listCats, createCat, updateSalary, deleteCat } from "../lib/api";
import CatForm from "../components/CatForm";
import CatsTable from "../components/CatsTable";

export default function Page() {
    const [cats, setCats] = useState([]);
    const [loading, setLoading] = useState(true);
    const [err, setErr] = useState("");
    const [creating, setCreating] = useState(false);

    async function load() {
        setLoading(true);
        setErr("");
        try {
            const data = await listCats();
            setCats(data);
        } catch (e) {
            setErr(e.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        load();
    }, []);

    async function handleCreate(payload) {
        setCreating(true);
        setErr("");
        try {
            await createCat(payload);
            await load();
        } catch (e) {
            setErr(e.message);
        } finally {
            setCreating(false);
        }
    }

    async function handleUpdateSalary(id, salary) {
        setErr("");
        try {
            await updateSalary(id, salary);
            await load();
        } catch (e) {
            setErr(e.message);
        }
    }

    async function handleDelete(id) {
        if (!confirm("Delete this cat?")) return;
        setErr("");
        try {
            await deleteCat(id);
            setCats((prev) => prev.filter((c) => c.id !== id));
        } catch (e) {
            setErr(e.message);
        }
    }

    return (
        <main className="container">
            <h1>Spy Cats Dashboard</h1>

            {err && <div className="alert">{err}</div>}

            <section className="card">
                <h2>Add new cat</h2>
                <CatForm onCreate={handleCreate} disabled={creating} />
            </section>

            <section className="card">
                <h2>All spy cats</h2>
                <CatsTable
                    cats={cats}
                    loading={loading}
                    onUpdateSalary={handleUpdateSalary}
                    onDelete={handleDelete}
                />
            </section>
        </main>
    );
}
