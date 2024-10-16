import { Avatar, Text, Stack, Flex,Box } from "@chakra-ui/react";
import logo from '../assets/logo.png';

function Header() {
    return (
        <Box>
            <Flex justify="space-between" align="center">
                <Flex align="center">
                    <Avatar src={logo} size='md' boxSize='3rem' margin='1rem' />
                    <Text fontWeight={600} fontSize={20} ml={2}>AutoGen Bot</Text>
                </Flex>
                <Flex cursor='pointer'>
                    <Avatar size='sm' name="Something New" bg="blue.200" margin='1rem' />
                </Flex>
            </Flex>
        </Box>
    );
}

export default Header;
