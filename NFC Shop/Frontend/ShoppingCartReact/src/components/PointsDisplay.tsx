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
            const storedCustomer = window.localStorage.getItem("customer");
            if (storedCustomer) {
                const parsedCustomer = JSON.parse(storedCustomer);
                setPoints(parsedCustomer.points);
                setCustomer(parsedCustomer);
            } else {
                setPoints(0);
                setCustomer(null);
            }
        }

        fetchPoints(); // Initial fetch

        const intervalId = setInterval(fetchPoints, 1000); // Run every second

        return () => clearInterval(intervalId); // Cleanup interval on component unmount
    }, [getPoints]);

    if (customer?.id === "") {
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