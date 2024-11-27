import React from 'react';
import { useShoppingCart } from "../context/ShoppingCartContext";
import { useEffect, useState } from 'react';

interface PointsDisplayProps {
    className?: string;
}

export function PointsDisplay({ className = "" }: PointsDisplayProps) {
    const { getPoints } = useShoppingCart()
    const [points, setPoints] = useState<number | null>(null);
    const [customer, setCustomer] = useState<{ id: string, points: number } | null>(null);

    useEffect(() => {
        async function fetchPoints() {
            await getPoints();
            setPoints(window.localStorage.getItem("customer") ? JSON.parse(window.localStorage.getItem("customer")!).points : 0);
            setCustomer(window.localStorage.getItem("customer") ? JSON.parse(window.localStorage.getItem("customer")!) : null);
        }
        fetchPoints();
    }, [getPoints]);

    if (customer === null) {
        return null;
    }

    return (
        <div className={`border rounded p-3 ${className}`}>
            <div className="ms-auto fw-bold fs-5">
                Points of the user {customer?.id}: {points !== null ? points : "scan..."}
            </div>
        </div>
    )
}