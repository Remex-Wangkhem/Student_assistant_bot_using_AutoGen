import { Avatar, Text, Stack, Flex } from "@chakra-ui/react";
import logo from '../assets/logo.png';

function Header() {
    return (
        <div className="m-2">
            <Flex justify="space-between" align="center">
                <Flex align="center">
                    <Avatar src={logo} size='md' boxSize='3rem' />
                    <Text fontWeight={600} fontSize={20} ml={2}>AutoGen Bot</Text>
                </Flex>
                <Flex cursor='pointer'>
                    <Avatar size='sm' name="Something New" bg="blue.200" />
                </Flex>
            </Flex>
        </div>
    );
}

export default Header;
