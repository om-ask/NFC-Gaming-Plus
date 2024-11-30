import { Button, Offcanvas, Stack } from 'react-bootstrap';
import { useShoppingCart } from "../context/ShoppingCartContext";
import { CartItem } from "./CartItem";
import storeItems from "../data/items.json"


type ShoppingCartProps = {
    isOpen: boolean
}

export function ShoppingCart({ isOpen }: ShoppingCartProps) {
    const { closeCart, cartItems, sendPoints } = useShoppingCart()

    function sumPoints(cartItems: any) {
        return cartItems.reduce((total: number, cartItem: { id: number; quantity: number; }) => {
            const item = storeItems.find(i => i.id === cartItem.id)
            return total + (item?.price || 0) * cartItem.quantity
        }, 0)
    }

    return (
        <Offcanvas show={isOpen} onHide={closeCart} placement="end">
            <Offcanvas.Header closeButton>
                <Offcanvas.Title>Cart</Offcanvas.Title>
            </Offcanvas.Header>
            <Offcanvas.Body>
                <Stack gap={3}>
                    {cartItems.map(item => (
                        <CartItem key={item.id} {...item} />
                    ))}
                    <div className="ms-auto fw-bold fs-5">
                        Total{" "}
                        {"Cost" + " " + (cartItems.reduce((total, cartItem) => {
                            const item = storeItems.find(i => i.id === cartItem.id)
                            return total + (item?.price || 0) * cartItem.quantity
                        }, 0))}
                    </div>
                </Stack>
                <Stack>
                    <Button
                        variant="outline-primary"
                        size="sm" onClick={() => {
                            const customer = window.localStorage.getItem("customer")
                            if (customer) {
                                const customerObj = JSON.parse(customer);
                                const points = sumPoints(cartItems);
                                const response = sendPoints(customerObj.id, "-" + points);
                                alert("points have been substracted");
                                window.localStorage.setItem("customer", '{"id":"","points":[]}');
                                const localCartItems = window.localStorage.getItem("shopping-cart");
                                if (localCartItems) {
                                    window.localStorage.setItem("shopping-cart", "[]");
                                }
                            }
                        }}>
                        Send
                    </Button>
                </Stack>

            </Offcanvas.Body>
        </Offcanvas>
    )
}