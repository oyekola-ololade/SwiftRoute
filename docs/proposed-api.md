# Proposed API Surface

> Specification only. No API implementation is included.

## Authentication

- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`

## Orders

- `GET /api/orders`
- `POST /api/orders`
- `GET /api/orders/{order_id}`
- `PATCH /api/orders/{order_id}`
- `POST /api/orders/{order_id}/approve`

## Shipments

- `GET /api/shipments`
- `POST /api/shipments`
- `GET /api/shipments/{shipment_id}`
- `GET /api/shipments/{shipment_id}/tracking`
- `POST /api/shipments/{shipment_id}/reconcile`

## Documents

- `GET /api/shipments/{shipment_id}/documents`
- `POST /api/documents/{document_id}/approve`
- `POST /api/documents/{document_id}/reject`
- `GET /api/documents/{document_id}/download`

## Payments

- `GET /api/invoices`
- `GET /api/invoices/{invoice_id}`
- `POST /api/invoices/{invoice_id}/record-payment`

## Administration

- `GET /api/audit-events`
- `GET /api/dashboard/metrics`

## Required implementation controls

- Authorization checks
- Input validation
- Idempotency on external writes
- Audit events
- Pagination and filtering
- Stable error contracts
- Rate limiting
- Tests for unauthorized cross-customer access

