import { Col, Row } from "react-bootstrap"
import storeItems from "../data/items.json"
import { StoreItem } from "../components/StoreItem"
import { PointsDisplay } from "../components/PointsDisplay"

export function Store() {
    return (
        <>
            <PointsDisplay className="fixed top-0 left-0 z-50"></PointsDisplay>
            <h1>Store</h1>
            <Row md={2} xs={1} lg={6} className="g-3">
                {storeItems.map(item => (
                    <Col key={item.id}>
                        <StoreItem {...item} />
                    </Col>
                ))}
            </Row>
        </>


    )
}