import React from 'react';
import { useShoppingCart } from "../context/ShoppingCartContext";
import { useEffect, useState } from 'react';

interface PointsDisplayProps {
    className?: string;
}

export function PointsDisplay({ className = "" }: PointsDisplayProps) {
    const { getPoints } = useShoppingCart()
    const [points, setPoints] = useState<number | null>(null);

    useEffect(() => {
        async function fetchPoints() {
            const result = await getPoints();
            setPoints(result);
        }
        fetchPoints();
    }, [getPoints]);

    return (
        <div className={` ${className}`}>
            <div className="ms-auto fw-bold fs-5">
                Points of the user: {points !== null ? points : "scan..."}
            </div>
        </div>
    )
}