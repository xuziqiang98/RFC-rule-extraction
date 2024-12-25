Example 1. (from RFC2132, DHICP)

IP Address Lease Time:
The code for this option is 51, and its length is 4.

Rule 1: chk_bf(length == 4, use(option))



Example 2. (from RFC2328, OSPF)

12.1.5. Advertising Router:
This field specifies the OSPF Router ID of the LSA's originator. For
router-LSAs, this field is identical to the Link State ID field.

Rule 2: chk_bf((LS type == router-LSAs && Advertise Router == Link State
ID)，use(Advertise Router))



Example 3. (from RFC427I, BGP)
OpenConfirm: If the local system receives a KEEPALIVE message
(KeepAliveMsg(Event 26)), the local system:

* restarts the HoldTimer and

* changes its state to Established

Rule 3: chk_bf(state == OpenConfrm && event == KeepAliveMsg),
set(state == Established))



Example 4. (from RFC 6286, BGP)

If the BGP Identifier field of the OPEN message is zero, or if it is the same
as the BGP Identifier of the local BGP speaker and the message is from an
internal peer, then the Error Subcode is set to “Bad BGP Identifier”

Rule 4: chk_bf((BGP Identifier == 0 || BGP Identifier == Local BGP Identifier)， set(Error Subcode, Bad BGP identifier))

