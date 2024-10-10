import { Box, Button, Divider, Text, VStack } from '@chakra-ui/react';

const SideBar = () => {
    return (
        <Box
            w="18rem"
            p="4"
            bg="gray.100"
            borderRightWidth="1px"
            h="full"
            display="flex"
            flexDirection="column"
        >
            <VStack spacing="4" align="start" flex="1">
                <Text fontSize="lg" fontWeight="bold">Tasks</Text>
                <Button colorScheme='teal' variant='outline'>Create Education Plan</Button>
                <Button colorScheme='teal' variant='outline'>Financial Aid</Button>
            </VStack>
            <Divider />
            <VStack spacing="4" align="start" flex="1" mt={4}>
                <Text fontSize="lg" fontWeight="bold">History</Text>
            </VStack>
        </Box>
    );
};

export default SideBar;
